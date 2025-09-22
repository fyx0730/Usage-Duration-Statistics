from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import GameSession, db
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """每次请求前连接数据库"""
    if db.is_closed():
        db.connect()

@app.after_request
def after_request(response):
    """每次请求后关闭数据库连接"""
    if not db.is_closed():
        db.close()
    return response

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """获取游戏会话列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        player_id = request.args.get('player_id')
        
        query = GameSession.select().order_by(GameSession.created_at.desc())
        
        if player_id:
            query = query.where(GameSession.player_id == player_id)
        
        # 分页
        sessions = query.paginate(page, per_page)
        
        result = []
        for session in sessions:
            result.append({
                'id': session.id,
                'player_id': session.player_id,
                'player_name': session.player_name,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration_seconds': session.duration_seconds,
                'created_at': session.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        logger.error(f"获取会话列表时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取使用统计"""
    try:
        date_str = request.args.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        # 指定日期统计
        day_sessions = GameSession.select().where(
            GameSession.start_time >= target_date,
            GameSession.start_time < target_date + timedelta(days=1),
            GameSession.duration_seconds.is_null(False)
        )
        
        day_total_time = sum(session.duration_seconds for session in day_sessions)
        day_session_count = day_sessions.count()
        
        # 本周统计
        week_start = target_date - timedelta(days=target_date.weekday())
        week_sessions = GameSession.select().where(
            GameSession.start_time >= week_start,
            GameSession.start_time < week_start + timedelta(days=7),
            GameSession.duration_seconds.is_null(False)
        )
        
        week_total_time = sum(session.duration_seconds for session in week_sessions)
        week_session_count = week_sessions.count()
        
        # 活跃玩家统计
        active_players = GameSession.select(
            GameSession.player_id,
            GameSession.player_name
        ).where(
            GameSession.start_time >= target_date,
            GameSession.start_time < target_date + timedelta(days=1)
        ).distinct()
        
        # 在线设备统计（最近5分钟内有活动的设备）
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        online_devices = GameSession.select(
            GameSession.player_id,
            GameSession.player_name
        ).where(
            (GameSession.end_time.is_null()) |
            (GameSession.start_time >= five_minutes_ago)
        ).distinct()
        
        return jsonify({
            'success': True,
            'data': {
                'selected_date': target_date.isoformat(),
                'day': {
                    'total_time_seconds': day_total_time,
                    'session_count': day_session_count,
                    'active_players': active_players.count()
                },
                'week': {
                    'total_time_seconds': week_total_time,
                    'session_count': week_session_count
                },
                'online_devices': online_devices.count()
            }
        })
        
    except Exception as e:
        logger.error(f"获取统计数据时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/players', methods=['GET'])
def get_players():
    """获取玩家列表及其使用统计"""
    try:
        # 获取所有玩家的统计信息
        players_query = GameSession.select(
            GameSession.player_id,
            GameSession.player_name,
        ).distinct()
        
        result = []
        for player in players_query:
            # 计算该玩家的总使用时长
            player_sessions = GameSession.select().where(
                GameSession.player_id == player.player_id,
                GameSession.duration_seconds.is_null(False)
            )
            
            total_time = sum(session.duration_seconds for session in player_sessions)
            session_count = player_sessions.count()
            
            # 最后一次游戏时间
            last_session = GameSession.select().where(
                GameSession.player_id == player.player_id
            ).order_by(GameSession.start_time.desc()).first()
            
            result.append({
                'player_id': player.player_id,
                'player_name': player.player_name,
                'total_time_seconds': total_time,
                'session_count': session_count,
                'last_played': last_session.start_time.isoformat() if last_session else None
            })
        
        # 按总使用时长排序
        result.sort(key=lambda x: x['total_time_seconds'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取玩家列表时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device-status', methods=['GET'])
def get_device_status():
    """获取设备实时状态"""
    try:
        # 获取所有设备的最新状态
        devices = []
        
        # 查询所有有记录的设备
        all_devices = GameSession.select(
            GameSession.player_id,
            GameSession.player_name
        ).distinct()
        
        for device in all_devices:
            # 查找最新的会话记录
            latest_session = GameSession.select().where(
                GameSession.player_id == device.player_id
            ).order_by(GameSession.start_time.desc()).first()
            
            # 判断设备状态
            status = "offline"
            current_session_id = None
            last_activity = None
            
            if latest_session:
                last_activity = latest_session.start_time
                if latest_session.end_time is None:
                    # 有未结束的会话，设备在线且使用中
                    status = "playing"
                    current_session_id = latest_session.id
                else:
                    # 检查最后活动时间，5分钟内算在线
                    time_diff = datetime.now() - latest_session.end_time
                    if time_diff.total_seconds() < 300:  # 5分钟
                        status = "online"
            
            devices.append({
                'player_id': device.player_id,
                'player_name': device.player_name,
                'status': status,
                'current_session_id': current_session_id,
                'last_activity': last_activity.isoformat() if last_activity else None
            })
        
        # 统计各状态数量
        status_count = {
            'online': len([d for d in devices if d['status'] == 'online']),
            'playing': len([d for d in devices if d['status'] == 'playing']),
            'offline': len([d for d in devices if d['status'] == 'offline'])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'devices': devices,
                'status_count': status_count,
                'total_devices': len(devices)
            }
        })
        
    except Exception as e:
        logger.error(f"获取设备状态时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/daily-chart', methods=['GET'])
def get_daily_chart():
    """获取每日使用时长图表数据"""
    try:
        days = int(request.args.get('days', 7))  # 默认7天
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 如果提供了具体的开始和结束日期
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
        else:
            # 使用默认的天数范围
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
        
        chart_data = []
        total_period_time = 0
        total_period_sessions = 0
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # 查询当天的会话数据
            day_sessions = GameSession.select().where(
                GameSession.start_time >= current_date,
                GameSession.start_time < current_date + timedelta(days=1),
                GameSession.duration_seconds.is_null(False)
            )
            
            total_time = sum(session.duration_seconds for session in day_sessions)
            session_count = day_sessions.count()
            
            total_period_time += total_time
            total_period_sessions += session_count
            
            chart_data.append({
                'date': current_date.isoformat(),
                'total_time_minutes': round(total_time / 60, 1),
                'total_time_hours': round(total_time / 3600, 2),
                'session_count': session_count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'daily_data': chart_data,
                'period_summary': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_days': days,
                    'total_time_minutes': round(total_period_time / 60, 1),
                    'total_time_hours': round(total_period_time / 3600, 2),
                    'total_sessions': total_period_sessions,
                    'avg_daily_minutes': round(total_period_time / 60 / days, 1) if days > 0 else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取图表数据时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device/<player_id>', methods=['DELETE'])
def delete_device(player_id):
    """删除设备及其所有相关数据"""
    try:
        # 删除该设备的所有游戏会话记录
        deleted_count = GameSession.delete().where(
            GameSession.player_id == player_id
        ).execute()
        
        logger.info(f"删除设备 {player_id} 的 {deleted_count} 条记录")
        
        return jsonify({
            'success': True,
            'message': f'成功删除设备 {player_id} 及其 {deleted_count} 条记录'
        })
        
    except Exception as e:
        logger.error(f"删除设备时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除单个游戏会话记录"""
    try:
        # 查找并删除指定的会话记录
        session = GameSession.get_by_id(session_id)
        session.delete_instance()
        
        logger.info(f"删除会话记录 {session_id}")
        
        return jsonify({
            'success': True,
            'message': f'成功删除会话记录 {session_id}'
        })
        
    except GameSession.DoesNotExist:
        return jsonify({'success': False, 'error': '会话记录不存在'}), 404
    except Exception as e:
        logger.error(f"删除会话记录时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/daily-summary', methods=['GET'])
def get_daily_summary():
    """获取按日期汇总的使用记录"""
    try:
        days = int(request.args.get('days', 7))  # 默认显示最近7天
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        daily_summary = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # 查询当天的会话数据
            day_sessions = GameSession.select().where(
                GameSession.start_time >= current_date,
                GameSession.start_time < current_date + timedelta(days=1)
            ).order_by(GameSession.start_time.desc())
            
            # 统计当天数据
            completed_sessions = [s for s in day_sessions if s.duration_seconds is not None]
            active_sessions = [s for s in day_sessions if s.duration_seconds is None]
            
            total_time = sum(session.duration_seconds for session in completed_sessions)
            
            # 获取当天活跃的设备
            active_devices = {}
            for session in day_sessions:
                device_id = session.player_id
                if device_id not in active_devices:
                    active_devices[device_id] = {
                        'player_name': session.player_name,
                        'sessions': 0,
                        'total_time': 0,
                        'last_activity': session.start_time
                    }
                
                active_devices[device_id]['sessions'] += 1
                if session.duration_seconds:
                    active_devices[device_id]['total_time'] += session.duration_seconds
                
                # 更新最后活动时间
                if session.start_time > active_devices[device_id]['last_activity']:
                    active_devices[device_id]['last_activity'] = session.start_time
            
            daily_summary.append({
                'date': current_date.isoformat(),
                'total_time_seconds': total_time,
                'total_time_minutes': round(total_time / 60, 1),
                'completed_sessions': len(completed_sessions),
                'active_sessions': len(active_sessions),
                'total_sessions': len(day_sessions),
                'active_devices_count': len(active_devices),
                'devices': list(active_devices.values())
            })
        
        # 按日期倒序排列（最新的在前面）
        daily_summary.reverse()
        
        return jsonify({
            'success': True,
            'data': daily_summary
        })
        
    except Exception as e:
        logger.error(f"获取每日汇总数据时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    """重定向到主页"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # 初始化数据库
    from models import init_db
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5001)