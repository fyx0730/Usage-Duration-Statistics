#!/usr/bin/env python3
"""
MQTT 连接测试脚本
"""

import paho.mqtt.client as mqtt
import json
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ 成功连接到 MQTT Broker")
        client.subscribe("game")
        logger.info("✅ 订阅主题: game")
        
        # 发送测试消息
        test_message = {
            "event": "game_start",
            "playerId": "test_player_001",
            "playerName": "测试玩家"
        }
        client.publish("game", json.dumps(test_message))
        logger.info("✅ 发送测试消息")
        
    else:
        logger.error(f"❌ 连接失败，错误代码: {rc}")
        error_messages = {
            1: "协议版本不正确",
            2: "客户端标识符无效",
            3: "服务器不可用",
            4: "用户名或密码错误",
            5: "未授权"
        }
        logger.error(f"错误详情: {error_messages.get(rc, '未知错误')}")

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        logger.info(f"✅ 收到消息: {message}")
    except Exception as e:
        logger.error(f"❌ 解析消息失败: {e}")

def on_disconnect(client, userdata, rc):
    logger.info("🔌 与 MQTT Broker 断开连接")

def test_mqtt_connection():
    """测试 MQTT 连接"""
    
    # 测试不同的连接方式
    configs = [
        {
            "name": "WebSocket 8084端口",
            "host": "mqtt.aimaker.space",
            "port": 8084,
            "use_ws": True,
            "ws_path": "/mqtt"
        },
        {
            "name": "标准TCP 1883端口", 
            "host": "mqtt.aimaker.space",
            "port": 1883,
            "use_ws": False,
            "ws_path": None
        },
        {
            "name": "SSL/TLS 8883端口",
            "host": "mqtt.aimaker.space", 
            "port": 8883,
            "use_ws": False,
            "ws_path": None
        }
    ]
    
    for config in configs:
        logger.info(f"\n🔄 测试 {config['name']}")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        try:
            # 设置用户名和密码
            client.username_pw_set("guest", "test")
            
            # 配置连接方式
            if config["use_ws"]:
                client.ws_set_options(path=config["ws_path"])
            
            logger.info(f"🔄 正在连接到 {config['host']}:{config['port']}")
            client.connect(config["host"], config["port"], 60)
            
            # 运行5秒测试
            client.loop_start()
            time.sleep(5)
            client.loop_stop()
            client.disconnect()
            
            logger.info(f"✅ {config['name']} 测试完成")
            
        except Exception as e:
            logger.error(f"❌ {config['name']} 连接失败: {e}")
        
        time.sleep(2)  # 等待2秒再测试下一个

if __name__ == "__main__":
    print("=== MQTT 连接测试 ===")
    test_mqtt_connection()
    print("测试完成")