async def get_chat_title(client, chat_id):
    try:
        entity = await client.get_entity(chat_id)

        if hasattr(entity, 'title'):
            if entity.username:
                return entity.username, 1, "(публичный канал)"
            return entity.title, 0, "(непубличный канал)"
        elif entity.username:
            return entity.username, 2, "(пользователь)"
        elif hasattr(entity, 'first_name'):
            return entity.first_name, 3, "(пользователь)"
        else:
            return None, -1, "не найдено"

    except Exception as e:
        print(f'Ошибка при получении названия чата: {e}')
        return None, -1, "ошибка"

