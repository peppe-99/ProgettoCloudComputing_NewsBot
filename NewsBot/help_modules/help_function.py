import asyncio


def get_intent(recognizer_result):
    intent = (
        sorted(
            recognizer_result.intents,
            key=recognizer_result.intents.get,
            reverse=True,
        )[:1][0]
        if recognizer_result.intents
        else None
    )
    return intent


def run_async_function(function):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    loop.run_until_complete(function)
    loop.close()
