import asyncio
import json
import aiormq
import aiormq.abc
import numpy_financial as npf
import pandas as pd
from settings import get_settings

settings = get_settings()


def count_npv(year: int, percent: float) -> float:
    df = pd.read_excel(settings.EXCEL_PATH, sheet_name='справочник')
    df = df.loc[df['год'] < int(year)]
    df['чистый доход'] = df['доход'].sub(df['затраты'], axis=0)
    initial_cash_flow = pd.Series([0])
    result = npf.npv(percent, pd.concat([initial_cash_flow, df['чистый доход']],
                                        ignore_index=True)).round(3)
    return result


async def on_message(message: aiormq.abc.DeliveredMessage):
    body_message = json.loads(message.body)
    response = str(count_npv(body_message.get('year'),
                             body_message.get('percent'))).encode('utf-8')
    await message.channel.basic_publish(
        response, routing_key=message.header.properties.reply_to,
        properties=aiormq.spec.Basic.Properties(
            correlation_id=message.header.properties.correlation_id
        ),
    )

    await message.channel.basic_ack(message.delivery.delivery_tag)


async def main():
    connection = await aiormq.connect(settings.AMQP_URL)
    channel = await connection.channel()
    declare_ok = await channel.queue_declare('rpc_queue')
    await channel.basic_consume(declare_ok.queue, on_message)


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
