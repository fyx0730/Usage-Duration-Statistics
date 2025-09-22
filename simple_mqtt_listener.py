#!/usr/bin/env python3
"""
简化的 MQTT 监听器，用于测试连接
"""

import paho.mqtt.client as mqtt
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ 成功连接到 MQTT Broker")
        client.subscribe("game")
        logger.info("✅ 订阅主题: game")
    else:
        logger.error(f"❌ 连接失败，错误代码: {rc}")

def on_message(client, userdata, msg):
    try:
        raw_message = msg.payload.decode()
        logger.info(f"📨 收到消息: {raw_message}")
        
        # 尝试解析 JSON
        try:
            message = json.loads(raw_message)
            logger.info(f"📋 JSON 解析成功: {message}")
        except json.JSONDecodeError:
            logger.info("📋 非 JSON 格式消息")
            
    except Exception as e:
        logger.error(f"❌ 处理消息出错: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"⚠️ 意外断开连接: {rc}")
    else:
        logger.info("✅ 正常断开连接")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # 设置认证
    client.username_pw_set("guest", "test")
    
    try:
        logger.info("🔄 正在连接到 MQTT Broker...")
        client.connect("mqtt.aimaker.space", 1883, 60)
        
        logger.info("🎧 开始监听消息... (按 Ctrl+C 退出)")
        client.loop_forever()
        
    except KeyboardInterrupt:
        logger.info("👋 收到退出信号")
    except Exception as e:
        logger.error(f"❌ 连接出错: {e}")
    finally:
        client.disconnect()
        logger.info("🔚 程序结束")

if __name__ == "__main__":
    main()