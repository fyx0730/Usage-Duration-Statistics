#!/usr/bin/env python3
"""
发送测试数据到 MQTT
"""

import paho.mqtt.client as mqtt
import json
import time
import random

def send_test_data():
    """发送测试游戏数据"""
    
    # 测试设备列表
    devices = [
        {"playerId": "娃娃机001", "playerName": "娃娃机（一楼大厅）"},
        {"playerId": "娃娃机002", "playerName": "娃娃机（二楼休息区）"},
        {"playerId": "娃娃机003", "playerName": "娃娃机（三楼游戏区）"},
        {"playerId": "游戏机001", "playerName": "街机（音游区）"},
        {"playerId": "游戏机002", "playerName": "赛车游戏机"}
    ]
    
    client = mqtt.Client()
    
    try:
        # 连接到 MQTT broker
        client.username_pw_set("guest", "test")
        client.connect("mqtt.aimaker.space", 1883, 60)
        client.loop_start()
        
        print("开始发送测试数据...")
        
        # 发送一些游戏开始事件
        for i, device in enumerate(devices):
            if random.random() > 0.3:  # 70% 概率设备在使用
                message = {
                    "event": "game_start",
                    "playerId": device["playerId"],
                    "playerName": device["playerName"]
                }
                
                client.publish("game", json.dumps(message))
                print(f"✅ 发送游戏开始: {device['playerName']}")
                time.sleep(1)
        
        time.sleep(2)
        
        # 随机结束一些游戏
        for device in devices:
            if random.random() > 0.5:  # 50% 概率结束游戏
                message = {
                    "event": "game_end",
                    "playerId": device["playerId"],
                    "playerName": device["playerName"]
                }
                
                client.publish("game", json.dumps(message))
                print(f"✅ 发送游戏结束: {device['playerName']}")
                time.sleep(1)
        
        print("测试数据发送完成!")
        
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ 发送测试数据失败: {e}")

if __name__ == "__main__":
    send_test_data()