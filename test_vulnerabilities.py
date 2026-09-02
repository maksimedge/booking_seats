import asyncio
from uuid import uuid4

import httpx

BASE_URL = 'http://localhost:8000/api/v1'
ADMIN_ID = '4c77e118-b051-41a5-b959-bf70a843d94d'
CAFE_ID = '7e8519c8-913d-472f-94ee-062f261a7b68'


async def get_token(client: httpx.AsyncClient) -> tuple[str, dict]:
    """Получить токен и заголовки."""
    login_data = {
        'login': 'admin_test@example.com',
        'password': 'AdminPass123',
    }
    response = await client.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f'Статус: {response.status_code}')
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get('access_token')
        print('✅ Токен получен')
        return token, {'Authorization': f'Bearer {token}'}
    print(f'❌ Ошибка логина: {response.text}')
    return None, None


async def test_negative_seats(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: отрицательное количество мест."""
    print('\n' + '=' * 60)
    print('3.1. Тест: отрицательное количество мест')
    print('=' * 60)

    table_data = {'seat_number': -5, 'description': 'Негативный тест'}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 422:
        print('✅ Защита сработала: отрицательное значение отклонено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_zero_seats(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: нулевое количество мест."""
    print('\n' + '=' * 60)
    print('3.2. Тест: нулевое количество мест')
    print('=' * 60)

    table_data = {'seat_number': 0, 'description': 'Нулевой тест'}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 422:
        print('✅ Защита сработала: нулевое значение отклонено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_max_seats(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: слишком большое количество мест."""
    print('\n' + '=' * 60)
    print('3.3. Тест: слишком большое количество мест (1000)')
    print('=' * 60)

    table_data = {'seat_number': 1000, 'description': 'Огромный стол'}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 422:
        print('✅ Защита сработала: слишком большое значение отклонено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_long_description(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: очень длинное описание."""
    print('\n' + '=' * 60)
    print('3.4. Тест: очень длинное описание (>500 символов)')
    print('=' * 60)

    long_description = 'A' * 600
    table_data = {'seat_number': 4, 'description': long_description}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 422:
        print('✅ Защита сработала: длинное описание отклонено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_fake_cafe(client: httpx.AsyncClient, headers: dict) -> None:
    """Тест: несуществующий cafe_id."""
    print('\n' + '=' * 60)
    print('3.5. Тест: несуществующий cafe_id')
    print('=' * 60)

    fake_cafe_id = str(uuid4())
    table_data = {'seat_number': 4, 'description': 'Тест с несуществующим кафе'}
    response = await client.post(
        f'{BASE_URL}/cafes/{fake_cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 404:
        print('✅ Защита сработала: кафе не найдено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_empty_body(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: пустое тело запроса."""
    print('\n' + '=' * 60)
    print('3.6. Тест: пустое тело запроса')
    print('=' * 60)

    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json={},
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 422:
        print('✅ Защита сработала: пустое тело отклонено')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_update_negative(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: обновление с отрицательным значением."""
    print('\n' + '=' * 60)
    print('3.7. Тест: обновление с отрицательным значением')
    print('=' * 60)

    table_data = {'seat_number': 4, 'description': 'Нормальный стол'}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    if response.status_code == 201:
        table = response.json()
        table_id = table['id']
        print(f'✅ Стол создан: id={table_id}')

        update_data = {'seat_number': -10}
        response = await client.patch(
            f'{BASE_URL}/cafes/{cafe_id}/tables/{table_id}',
            json=update_data,
            headers=headers,
        )
        print(f'Статус: {response.status_code}')
        if response.status_code == 422:
            print('✅ Защита сработала: отрицательное значение отклонено')
        else:
            print(f'⚠️ Неожиданный ответ: {response.text}')
    else:
        print('❌ Не удалось создать стол для теста')


async def test_no_token(client: httpx.AsyncClient, cafe_id: str) -> None:
    """Тест: доступ без токена."""
    print('\n' + '=' * 60)
    print('3.8. Тест: доступ без токена')
    print('=' * 60)

    response = await client.get(f'{BASE_URL}/cafes/{cafe_id}/tables')
    print(f'Статус: {response.status_code}')
    if response.status_code == 401:
        print('✅ Защита сработала: без токена доступ запрещён')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_invalid_token(client: httpx.AsyncClient, cafe_id: str) -> None:
    """Тест: невалидный токен."""
    print('\n' + '=' * 60)
    print('3.9. Тест: невалидный токен')
    print('=' * 60)

    bad_headers = {'Authorization': 'Bearer invalid_token'}
    response = await client.get(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        headers=bad_headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 401:
        print('✅ Защита сработала: невалидный токен отклонён')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_fake_table(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: несуществующий table_id."""
    print('\n' + '=' * 60)
    print('3.10. Тест: несуществующий table_id')
    print('=' * 60)

    fake_table_id = str(uuid4())
    response = await client.get(
        f'{BASE_URL}/cafes/{cafe_id}/tables/{fake_table_id}',
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 404:
        print('✅ Защита сработала: стол не найден')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_update_fake(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: обновление несуществующего стола."""
    print('\n' + '=' * 60)
    print('3.11. Тест: обновление несуществующего стола')
    print('=' * 60)

    fake_table_id = str(uuid4())
    update_data = {'seat_number': 10}
    response = await client.patch(
        f'{BASE_URL}/cafes/{cafe_id}/tables/{fake_table_id}',
        json=update_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 404:
        print('✅ Защита сработала: стол не найден')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_sql_injection(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: SQL Injection в описании."""
    print('\n' + '=' * 60)
    print('3.12. Тест: SQL Injection в описании')
    print('=' * 60)

    sql_injection = "'; DROP TABLE tables; --"
    table_data = {'seat_number': 4, 'description': sql_injection}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 201:
        print('✅ SQL Injection не сработал')
        check_response = await client.get(
            f'{BASE_URL}/cafes/{cafe_id}/tables',
            headers=headers,
        )
        if check_response.status_code == 200:
            print('✅ Таблица существует — SQL Injection не прошёл')
        else:
            print('❌ Возможно, SQL Injection сработал!')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_xss(client: httpx.AsyncClient, cafe_id: str, headers: dict) -> None:
    """Тест: XSS в описании."""
    print('\n' + '=' * 60)
    print('3.13. Тест: XSS в описании')
    print('=' * 60)

    xss_payload = "<script>alert('XSS')</script>"
    table_data = {'seat_number': 4, 'description': xss_payload}
    response = await client.post(
        f'{BASE_URL}/cafes/{cafe_id}/tables',
        json=table_data,
        headers=headers,
    )
    print(f'Статус: {response.status_code}')
    if response.status_code == 201:
        table = response.json()
        print(f'✅ Стол создан с XSS-payload: {table["description"]}')
        print('⚠️ Проверь, что в ответе теги экранируются (не отображаются как HTML)')
    else:
        print(f'⚠️ Неожиданный ответ: {response.text}')


async def test_vulnerabilities() -> None:
    """Основная функция запуска всех тестов."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        token, headers = await get_token(client)
        if not token:
            return

        cafe_id = CAFE_ID

        await test_negative_seats(client, cafe_id, headers)
        await test_zero_seats(client, cafe_id, headers)
        await test_max_seats(client, cafe_id, headers)
        await test_long_description(client, cafe_id, headers)
        await test_fake_cafe(client, headers)
        await test_empty_body(client, cafe_id, headers)
        await test_update_negative(client, cafe_id, headers)
        await test_no_token(client, cafe_id)
        await test_invalid_token(client, cafe_id)
        await test_fake_table(client, cafe_id, headers)
        await test_update_fake(client, cafe_id, headers)
        await test_sql_injection(client, cafe_id, headers)
        await test_xss(client, cafe_id, headers)


if __name__ == '__main__':
    asyncio.run(test_vulnerabilities())
