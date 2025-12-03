"""
RabbitMQ消息生产者服务
负责与RabbitMQ服务器建立连接并发送告警消息
"""

import pika
import json
import time
import logging
from typing import Dict, Any
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from ..config.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    RABBITMQ_VIRTUAL_HOST,
    RABBITMQ_EXCHANGE,
    RABBITMQ_EXCHANGE_TYPE,
    RABBITMQ_QUEUE,
    RABBITMQ_ROUTING_KEY,
    RABBITMQ_MESSAGE_DURABLE,
    RABBITMQ_CONNECTION_RETRIES,
    RABBITMQ_CONNECTION_RETRY_DELAY
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """RabbitMQ消息生产者类"""

    def __init__(self):
        """初始化RabbitMQ生产者"""
        self.connection = None
        self.channel = None
        self.connected = False
        # 延迟连接，在实际使用时才创建连接
        # self._connect()

    def _connect(self):
        """建立与RabbitMQ服务器的连接"""
        retry_count = 0

        while retry_count < RABBITMQ_CONNECTION_RETRIES:
            try:
                # 创建连接参数
                credentials = pika.PlainCredentials(
                    username=RABBITMQ_USERNAME,
                    password=RABBITMQ_PASSWORD
                )

                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    virtual_host=RABBITMQ_VIRTUAL_HOST,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )

                # 建立连接
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                # 声明交换机
                self.channel.exchange_declare(
                    exchange=RABBITMQ_EXCHANGE,
                    exchange_type=RABBITMQ_EXCHANGE_TYPE,
                    durable=True
                )

                # 声明队列
                self.channel.queue_declare(
                    queue=RABBITMQ_QUEUE,
                    durable=RABBITMQ_MESSAGE_DURABLE
                )

                # 绑定队列到交换机
                self.channel.queue_bind(
                    queue=RABBITMQ_QUEUE,
                    exchange=RABBITMQ_EXCHANGE,
                    routing_key=RABBITMQ_ROUTING_KEY
                )

                self.connected = True
                logger.info("成功连接到RabbitMQ服务器")
                return

            except (AMQPConnectionError, AMQPChannelError) as e:
                retry_count += 1
                logger.error(f"连接RabbitMQ失败 (尝试 {retry_count}/{RABBITMQ_CONNECTION_RETRIES}): {str(e)}")

                if retry_count < RABBITMQ_CONNECTION_RETRIES:
                    logger.info(f"将在 {RABBITMQ_CONNECTION_RETRY_DELAY} 秒后重试...")
                    time.sleep(RABBITMQ_CONNECTION_RETRY_DELAY)
                else:
                    logger.error("达到最大重试次数，连接失败")
                    self.connected = False
                    raise

    def _ensure_connection(self):
        """确保连接有效，无效则重新连接"""
        if not self.connected or not self.connection or self.connection.is_closed or not self.channel or self.channel.is_closed:
            logger.info("RabbitMQ连接未建立或已关闭，建立连接...")
            self._connect()

    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        发送消息到RabbitMQ队列

        Args:
            message: 要发送的消息字典

        Returns:
            bool: 消息发送是否成功
        """
        try:
            # 确保连接有效
            self._ensure_connection()

            # 将消息序列化为JSON
            message_body = json.dumps(message, ensure_ascii=False, default=str)

            # 发送消息
            self.channel.basic_publish(
                exchange=RABBITMQ_EXCHANGE,
                routing_key=RABBITMQ_ROUTING_KEY,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    content_type='application/json',
                    content_encoding='utf-8'
                )
            )

            logger.info(f"消息发送成功: {message_body[:100]}...")
            return True

        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            # 重置连接状态，下次发送时会重新连接
            self.connected = False
            return False

    def close(self):
        """关闭RabbitMQ连接"""
        if self.connected and self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                self.connected = False
                logger.info("RabbitMQ连接已关闭")
            except Exception as e:
                logger.error(f"关闭RabbitMQ连接失败: {str(e)}")


# 创建全局RabbitMQ生产者实例
rabbitmq_producer = RabbitMQProducer()
