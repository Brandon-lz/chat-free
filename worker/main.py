
from src.redis.config import Redis
import asyncio

from src.redis.cache import Cache
from src.redis.config import Redis
from src.redis.stream import StreamConsumer
import os
from src.schema.chat import Message
from src.redis.producer import Producer

from openai.error import APIConnectionError
from openai.error import RateLimitError

from src.model.gptj import GPT
from src.model.gpt3 import GPT3
from src.model.gpt35_chat import GPT35
from logs import logger


redis = Redis()


async def main():
    json_client = redis.create_rejson_connection()
    redis_client = await redis.create_connection()
    consumer = StreamConsumer(redis_client,consumer_name='worker02')
    await consumer.init_consumer(stream_channel='message_channel_new')
    cache = Cache(json_client)
    producer = Producer(redis_client)

    print("Stream consumer started")
    print("Stream waiting for new messages")
    
    consumer_havent_ack = True  

    while True:
        # 等待新的消息
        response = await consumer.consume_stream(stream_channel="message_channel_new", count=1, block=-0,consume_not_ack=consumer_havent_ack)
        print(response)
        if response:
            for stream, messages in response:
                # Get message from stream, and extract token, message data and message id
                for message in messages:
                    message_id = message[0]
                    token = [k.decode('utf-8')
                             for k, v in message[1].items()][0]
                    message = [v.decode('utf-8')
                               for k, v in message[1].items()][0]
                    print(token)

                    # Create a new message instance and add to cache, specifying the source as human
                    msg = Message(msg=message)
                    # print(msg.json())
                    await cache.add_message_to_cache(token=token, source="human", message_data=msg.dict())

                    # Get chat history from cache
                    data = await cache.get_chat_history(token=token,count=20)
                    if data==None:
                        continue

                    # Clean message input and send to query
                    message_data = data

                    input = ["" + i['msg'] for i in message_data]
                    input = "".join(input)
                    # print('input')
                    # print(input)
                    
                    
                    # res = GPT().query(input=input)
                    robot_error = False
                    try:
                        # res = GPT35().query(input=input)
                        res,total_tokens = GPT35().query(input=input)
                    except APIConnectionError as err:
                        res = str(err)
                    except RateLimitError as err:
                        res = str(err)
                    except Exception as err:
                        logger.error(type(err))
                        logger.error(err)
                        robot_error = True
                        res = 'robot error!'
                    finally:
                        try:
                            total_tokens=total_tokens
                        except:
                            total_tokens=0
                    logger.debug(f'robot res:{res}')
                    res = res.split('Bot:')[-1]
                    # robot messages
                    if robot_error:
                        msg = Message(
                            msg=' ',
                            total_tokens=0
                            )
                    else:
                        msg = Message(
                            msg=res,
                            total_tokens=total_tokens
                        )

                    # print(msg)
                    
                    stream_data = {}
                    stream_data[str(token)] = str(msg.dict())
                    
                    await producer.add_to_stream(stream_data, f"response_channel_new-{token}")
                    await cache.add_message_to_cache(token=token, source="bot", message_data=msg.dict())
                    

                # Delete messaage from queue after it has been processed
                # await consumer.delete_message(stream_channel="message_channel_new", message_id=message_id)    # 从redis队列中删除消息
                await consumer.ack_message(stream_channel="message_channel_new", message_id=message_id)    # 从redis队列中删除消息
        else:
            consumer_havent_ack = False

if __name__ == "__main__":
    logger.info('worker start...')
    asyncio.run(main())



# Manufacturing has created stricter requirements for the interaction and cooperation of robots，which have been difficult for traditional robot interaction technologies to meet．In this paper，a new guide control technology is proposed that uses a handheld navigator based on force/torque recognition，and a guide control mode that realizes the conversion of fast and slow control was developed．The original data of the navigator was read and analyzed，its own coordinate system obtained，the mapping relationship with the robot established，and the quantitative relationship between the output data and the force/torque was obtained by calibration．Then，to reduce the influence of physiological jitter and noise of the operators in the process of manipulation，Kalman filter was introduced to optimize the state of operators．To realize the transformation of the multi-control mode，the variable admittance control model was established．The change rate of the interaction force was obtained using least square method，the admittance parameters in the process of the human-robot interaction were determined，and then the control mode in accordance with the operator’s intention was selected．Finally，the feasibility and universality of the method in a humanrobot interaction application was experimentally verified．