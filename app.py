from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mangaApp"
DB_USER = "root"
DB_PASSWORD = "root"

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    if connection_pool:
        print("Connection pool created successfully.")
except Exception as ex:
    print(f"Error creating connection pool: {ex}")
    connection_pool = None

def execute_query(query, params=None, cursor_factory=None, fetch_results=True):
    if not connection_pool:
        raise Exception("Database connection pool not initialized")

    connection = None
    try:
        connection = connection_pool.getconn()

        with connection.cursor(cursor_factory=cursor_factory) as cursor:
            cursor.execute(query, params)

            if fetch_results:
                result = cursor.fetchall()
            else:
                result = None

            connection.commit()
            return result

    except Exception as e:
        if connection:
            connection.rollback()
        raise e

    finally:
        if connection:
            connection_pool.putconn(connection)

@app.route('/userManga', methods=['GET'])
def get_user_manga():
    try:
        user_id = request.args.get('userId')
        manga_id = request.args.get('mangaId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        if manga_id:
            query = """
            SELECT 
                us.userId AS "userId",
                us.mangaId AS "mangaId",
                us.link AS "link",
                us.altLink AS "altLink",
                us.userTitle AS "userTitle",
                us.currentChapter AS "currentChapter",
                us.readingStatus AS "readingStatus",
                TO_CHAR(us.dateAdded, 'YYYY-MM-DD') AS "dateAdded",
                us.isFavorite AS "isFavorite",
                us.userRating AS "userRating",
                us.notes AS "notes",
                m.mangadexId AS "mangadexId",
                m.coverUrl AS "coverUrl",
                TO_CHAR(m.publicationDate, 'YYYY-MM-DD')  AS "publicationDate",
                m.synopsis AS "synopsis"
            FROM 
                UserManga us
            JOIN 
                Manga m ON us.mangaId = m.mangaId
            WHERE 
                us.userId = %s AND m.mangaId = %s;
            """
            params = (user_id, manga_id)
            user_mangas = execute_query(query, params=params, cursor_factory=RealDictCursor)

            if user_mangas:
                return jsonify(user_mangas[0])
            else:
                return jsonify({"error": "Manga not found"}), 404
        else:
            query = """
            SELECT 
                us.userId AS "userId",
                us.mangaId AS "mangaId",
                us.link AS "link",
                us.altLink AS "altLink",
                us.userTitle AS "userTitle",
                us.currentChapter AS "currentChapter",
                us.readingStatus AS "readingStatus",
                TO_CHAR(us.dateAdded, 'YYYY-MM-DD') AS "dateAdded",
                us.isFavorite AS "isFavorite",
                us.userRating AS "userRating",
                us.notes AS "notes",
                m.mangadexId AS "mangadexId",
                m.coverUrl AS "coverUrl",
                TO_CHAR(m.publicationDate, 'YYYY-MM-DD')  AS "publicationDate",
                m.synopsis AS "synopsis"
            FROM 
                UserManga us
            JOIN 
                Manga m ON us.mangaId = m.mangaId
            WHERE 
                us.userId = %s;
            """
            params = (user_id,)
            user_mangas = execute_query(query, params=params, cursor_factory=RealDictCursor)

            return jsonify(user_mangas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/userManga/favorites', methods=['GET'])
def get_user_manga_favorites():
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        query = """
        SELECT 
            us.userId AS "userId",
            us.mangaId AS "mangaId",
            us.link AS "link",
            us.altLink AS "altLink",
            us.userTitle AS "userTitle",
            us.currentChapter AS "currentChapter",
            us.readingStatus AS "readingStatus",
            TO_CHAR(us.dateAdded, 'YYYY-MM-DD') AS "dateAdded",
            us.isFavorite AS "isFavorite",
            us.userRating AS "userRating",
            us.notes AS "notes",
            m.mangadexId AS "mangadexId",
            m.coverUrl AS "coverUrl",
            TO_CHAR(m.publicationDate, 'YYYY-MM-DD')  AS "publicationDate",
            m.synopsis AS "synopsis"
        FROM 
            UserManga us
        JOIN 
            Manga m ON us.mangaId = m.mangaId
        WHERE 
            us.userId = %s and us.isFavorite = true;
        """
        params = (user_id,)
        user_mangas = execute_query(query, params=params, cursor_factory=RealDictCursor)

        return jsonify(user_mangas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/userManga', methods=['POST'])
def save_user_manga_with_manga():
    try:
        data = request.get_json()

        user_id = data.get("userId")
        manga_id = data.get("mangaId")
        mangadex_id = data.get("mangadexId")
        cover_url = data.get("coverUrl")
        publication_date = data.get("publicationDate")
        synopsis = data.get("synopsis")
        link = data.get("link")
        alt_link = data.get("altLink")
        user_title = data.get("userTitle")
        current_chapter = data.get("currentChapter")
        reading_status = data.get("readingStatus")
        date_added = data.get("dateAdded")
        is_favorite = data.get("isFavorite")
        user_rating = data.get("userRating")
        notes = data.get("notes")

        query = """
            SELECT save_user_manga_with_manga(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        params = (
            user_id, manga_id, mangadex_id, cover_url,
            publication_date, synopsis, link, alt_link, user_title,
            current_chapter, reading_status, date_added, is_favorite,
            user_rating, notes
        )

        execute_query(query, params=params, fetch_results=False)

        return jsonify({"message": "UserManga and Manga saved successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/userManga', methods=['PUT'])
def update_user_manga_with_manga():
    try:
        data = request.get_json()

        user_id = data.get("userId")
        manga_id = data.get("mangaId")
        mangadex_id = data.get("mangadexId")
        cover_url = data.get("coverUrl")
        publication_date = data.get("publicationDate")
        synopsis = data.get("synopsis")
        link = data.get("link")
        alt_link = data.get("altLink")
        user_title = data.get("userTitle")
        current_chapter = data.get("currentChapter")
        reading_status = data.get("readingStatus")
        date_added = data.get("dateAdded")
        is_favorite = data.get("isFavorite")
        user_rating = data.get("userRating")
        notes = data.get("notes")

        query = """
            SELECT update_user_manga_with_manga(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        params = (
            user_id, manga_id, mangadex_id, cover_url,
            publication_date, synopsis, link, alt_link, user_title,
            current_chapter, reading_status, date_added, is_favorite,
            user_rating, notes
        )

        execute_query(query, params=params, fetch_results=False)

        return jsonify({"message": "UserManga and Manga updated successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/allUsers', methods=['GET'])
def get_all_users():
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        query = """
        SELECT 
            userId as "userId", 
            username as "userName"
        FROM 
            UserApp
        WHERE 
            userId != %s
        order by userId;
        """
        params = (user_id,)
        users = execute_query(query, params=params, cursor_factory=RealDictCursor)

        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user', methods=['GET'])
def get_user():
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        query = """
        SELECT 
            userId as "userId", 
            username as "userName"
        FROM 
            UserApp
        WHERE 
            userId = %s
        order by userId;
        """
        params = (user_id,)
        users = execute_query(query, params=params, cursor_factory=RealDictCursor)

        return jsonify(users[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sharedLink', methods=['POST'])
def save_shared_link():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        sender = data.get("sender")
        recipient = data.get("recipient")

        if not sender or not recipient:
            return jsonify({"error": "Sender and Recipient objects are required"}), 400

        sender_id = sender.get("userId")
        recipient_id = recipient.get("userId")
        if not sender_id or not recipient_id:
            return jsonify({"error": "SenderId and RecipientId are required fields"}), 400

        link_ = data.get("link_")
        alt_link = data.get("altLink")
        manga = data.get("manga")

        if not manga:
            return jsonify({"error": "Manga object is required"}), 400

        manga_id = manga.get("mangaId")
        if not all([sender_id, recipient_id, manga_id, link_]):
            return jsonify({"error": "Missing required fields"}), 400

        query = """
        INSERT INTO SharedLink (senderId, recipientId, mangaId, link_, altLink, state_received)
        VALUES (%s, %s, %s, %s, %s, 0)
        """
        params = (sender_id, recipient_id, manga_id, link_, alt_link)
        execute_query(query, params=params, fetch_results=False)

        return jsonify({
            "message": "SharedLink saved successfully."
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sharedLink', methods=['GET'])
def get_all_shared_links():
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        query = """
        SELECT 
            sharedLinkId as "sharedLinkId", 
            senderId as "senderId", 
            recipientId as "recipientId", 
            mangaId as "mangaId", 
            link_ as "link_", 
            altLink as "altLink"
        FROM 
            SharedLink
        WHERE 
            recipientId = %s and state_received = 0
        ORDER BY sharedLinkId;
        """
        params = (user_id,)
        shared_links = execute_query(query, params=params, cursor_factory=RealDictCursor)

        for link in shared_links:
            manga_id = link.pop('mangaId', None)
            if manga_id:
                manga_query = """
                SELECT 
                    mangaId as "mangaId", 
                    mangadexId as "mangadexId", 
                    originalTitle as "title", 
                    coverUrl as "coverUrl", 
                    TO_CHAR(publicationDate, 'YYYY-MM-DD') AS "publicationDate",
                    synopsis as "synopsis"
                FROM Manga
                WHERE mangaId = %s;
                """
                manga_params = (manga_id,)
                manga = execute_query(manga_query, params=manga_params, cursor_factory=RealDictCursor)
                link['manga'] = manga[0] if manga else None
            else:
                link['manga'] = None

            sender_id = link.pop('senderId', None)
            if sender_id:
                sender_query = """
                SELECT 
                    userId as "userId", 
                    userName as "userName"
                FROM UserApp
                WHERE userId = %s;
                """
                sender_params = (sender_id,)
                sender = execute_query(sender_query, params=sender_params, cursor_factory=RealDictCursor)
                link['sender'] = sender[0] if sender else None
            else:
                link['sender'] = None

            recipient_id = link.pop('recipientId', None)
            if recipient_id:
                recipient_query = """
                SELECT 
                    userId as "userId", 
                    userName as "userName"
                FROM UserApp
                WHERE userId = %s;
                """
                recipient_params = (recipient_id,)
                recipient = execute_query(recipient_query, params=recipient_params, cursor_factory=RealDictCursor)
                link['recipient'] = recipient[0] if recipient else None
            else:
                link['recipient'] = None

        return jsonify(shared_links)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sharedLink', methods=['PUT'])
def update_shared_link():
    try:
        data = request.get_json()

        sender = data.get("sender")
        recipient = data.get("recipient")
        sender_id = sender.get("userId")
        recipient_id = recipient.get("userId")
        manga = data.get("manga")
        manga_id = manga.get("mangaId")

        query = """
            update sharedlink
            set state_received = 1
            where senderId = %s and recipientId = %s and mangaId = %s
        """

        params = (sender_id, recipient_id, manga_id)
        print(params)
        execute_query(query, params=params, fetch_results=False)

        return jsonify({"message": "sharedLink updated successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/statistics', methods=['GET'])
def get_user_statistics():
    try:
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({"error": "userId is required"}), 400

        query = """
        SELECT 
            COUNT(CASE WHEN readingStatus = 'Reading' THEN 1 END) AS "reading",
            COUNT(CASE WHEN readingStatus = 'Completed' THEN 1 END) AS "completed",
            COUNT(CASE WHEN readingStatus = 'Dropped' THEN 1 END) AS "dropped",
            COUNT(CASE WHEN readingStatus = 'On Hold' THEN 1 END) AS "onHold"
        FROM 
            UserManga
        WHERE 
            userId = %s;
        """
        params = (user_id,)
        result = execute_query(query, params=params, cursor_factory=RealDictCursor)

        return jsonify(result[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/collection', methods=['POST'])
def create_collection():
    try:
        data = request.get_json()

        user_id = data.get("userId")
        collection_name = data.get("collectionName")

        if not user_id or not collection_name:
            return jsonify({"error": "userId and collectionName are required."}), 400

        from datetime import date
        date_created = date.today()
        date_last_modified = date_created

        query = """
            INSERT INTO Collection (userId, collectionName, dateCreated, dateLastModified)
            VALUES (%s, %s, %s, %s)
        """

        params = (user_id, collection_name, date_created, date_last_modified)

        execute_query(query, params=params, fetch_results=False)

        return jsonify({
            "message": "Collection created successfully."
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/collection', methods=['GET'])
def get_collection():
    try:
        user_id = request.args.get("userId")

        if not user_id:
            return jsonify({"error": "userId is required."}), 400

        query = """
            SELECT 
                userId as "userId",
                collectionId AS "collectionId",
                collectionName AS "collectionName",
                TO_CHAR(dateCreated, 'YYYY-MM-DD') AS "dateCreated",
                TO_CHAR(dateLastModified, 'YYYY-MM-DD') AS "dateLastModified"
            FROM 
                Collection
            WHERE 
                userId = %s
            ORDER BY 
                dateCreated DESC;
        """

        params = (user_id,)

        collections = execute_query(query, params=params, cursor_factory=RealDictCursor)

        return jsonify(collections), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mangaCollection', methods=['GET'])
def get_manga_collection():
    try:
        user_id = request.args.get('userId')
        collection_id = request.args.get('collectionId')

        if not user_id or not collection_id:
            return jsonify({"error": "userId and collectionId are required"}), 400

        collection_query = """
        SELECT 
            c.collectionId as "collectionId", 
            c.userId as "userId", 
            c.collectionName as "collectionName", 
            TO_CHAR(c.dateCreated, 'YYYY-MM-DD') AS "dateCreated",
            TO_CHAR(c.dateLastModified, 'YYYY-MM-DD') AS "dateLastModified"
        FROM Collection c
        WHERE c.userId = %s AND c.collectionId = %s;
        """
        collection_params = (user_id, collection_id)
        collection_result = execute_query(collection_query, params=collection_params, cursor_factory=RealDictCursor)

        if not collection_result:
            return jsonify({"error": "Collection not found for the specified userId and collectionId"}), 404

        collection = collection_result[0]

        user_query = """
        SELECT 
            u.userId as "userId", 
            u.username as "userName"
        FROM UserApp u
        WHERE u.userId = %s;
        """
        user_params = (user_id,)
        user_result = execute_query(user_query, params=user_params, cursor_factory=RealDictCursor)

        if not user_result:
            return jsonify({"error": "User not found"}), 404

        user = user_result[0]

        manga_query = """
        SELECT 
            m.mangaId as "mangaId", 
            m.mangadexId as "mangadexId", 
            m.originalTitle as "title", 
            m.coverUrl as "coverUrl", 
            TO_CHAR(m.publicationDate, 'YYYY-MM-DD') AS "publicationDate",
            m.synopsis as "synopsis"
        FROM Manga m
        JOIN UserManga um ON um.mangaId = m.mangaId
		join mangaCollection mc on mc.mangaId = m.mangaId
		where um.userId = %s and mc.collectionId = %s
        """
        manga_params = (user_id, collection_id)
        manga_result = execute_query(manga_query, params=manga_params, cursor_factory=RealDictCursor)

        manga_collections = []

        for manga in manga_result:
            manga_collections.append({
                "collection": {
                    "collectionId": collection["collectionId"],
                    "userId": collection["userId"],
                    "collectionName": collection["collectionName"],
                    "dateCreated": collection["dateCreated"],
                    "dateLastModified": collection["dateLastModified"]
                },
                "user": {
                    "userId": user["userId"],
                    "userName": user["userName"]
                },
                "manga": manga
            })

        return jsonify(manga_collections)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/collection/<int:manga_id>/<int:user_id>', methods=['GET'])
def get_collections_by_manga_id_and_user_id(manga_id, user_id):
    try:
        collection_query = """
        SELECT 
            c.collectionId AS "collectionId", 
            c.userId AS "userId", 
            c.collectionName AS "collectionName", 
            TO_CHAR(c.dateCreated, 'YYYY-MM-DD') AS "dateCreated",
            TO_CHAR(c.dateLastModified, 'YYYY-MM-DD') AS "dateLastModified"
        FROM Collection c
        WHERE c.userId = %s AND EXISTS (
            SELECT 1 
            FROM mangaCollection mc
            WHERE mc.mangaId = %s AND mc.collectionId = c.collectionId
        );
        """
        collection_params = (user_id, manga_id)

        collection_result = execute_query(
            collection_query,
            params=collection_params,
            cursor_factory=RealDictCursor
        )

        if not collection_result:
            return jsonify({"error": "No collections found for the specified mangaId and userId"}), 404

        return jsonify(collection_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/mangaCollection', methods=['POST'])
def create_collection_manga():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid or missing JSON data"}), 400

        if not isinstance(data,
                          dict) or 'mangaId' not in data or 'userId' not in data or 'collectionIdList' not in data:
            return jsonify({"error": "Invalid request structure. Expected mangaId, userId, and collectionIdList"}), 400

        manga_id = data.get('mangaId')
        user_id = data.get('userId')
        collection_id_list = data.get('collectionIdList')

        delete_query = """
        DELETE FROM mangaCollection
        WHERE mangaId = %s AND userId = %s;
        """
        delete_params = (manga_id, user_id)
        execute_query(delete_query, params=delete_params, cursor_factory=RealDictCursor, fetch_results=False)

        if not isinstance(collection_id_list, list) or not collection_id_list:
            return jsonify({"message": "collectionIdList emptied"}), 201

        for collection_id in collection_id_list:
            insert_query = """
            INSERT INTO mangaCollection (userId, collectionId, mangaId)
            VALUES (%s, %s, %s)
            ON CONFLICT (userId, collectionId, mangaId) DO NOTHING;
            """
            insert_params = (user_id, collection_id, manga_id)
            execute_query(insert_query, params=insert_params, cursor_factory=RealDictCursor, fetch_results=False)

        return jsonify({
            "message": "Manga collections processed successfully."
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/mangaCollection', methods=['DELETE'])
def delete_collection_manga():
    try:
        user_id = request.args.get('userId')
        collection_id = request.args.get('collectionId')
        manga_id = request.args.get('mangaId')

        if not user_id or not collection_id or not manga_id:
            return jsonify({"error": "Missing userId, collectionId, or mangaId"}), 400

        collection_manga_query = """
        DELETE FROM mangaCollection
        WHERE userId = %s AND collectionId = %s AND mangaId = %s;
        """
        collection_manga_params = (user_id, collection_id, manga_id)

        execute_query(collection_manga_query, params=collection_manga_params, cursor_factory=RealDictCursor, fetch_results=False)

        return jsonify({
            "message": "Manga Collection deleted successfully."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/userManga', methods=['DELETE'])
def delete_user_manga():
    try:
        user_id = request.args.get("userId")
        manga_id = request.args.get("mangaId")

        query = """
            DELETE FROM UserManga WHERE userId = %s AND mangaId = %s;
        """
        params = (user_id, manga_id)

        execute_query(query, params=params, fetch_results=False)

        return jsonify({"message": "UserManga deleted successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/collection', methods=['DELETE'])
def delete_collection():
    try:
        user_id = request.args.get("userId")
        collection_id = request.args.get("collectionId")

        if not user_id or not collection_id:
            return jsonify({"error": "userId and collectionName are required."}), 400

        query = """
            DELETE FROM Collection WHERE userId = %s AND collectionId = %s;
        """

        params = (user_id, collection_id)

        execute_query(query, params=params, fetch_results=False)

        return jsonify({
            "message": "Collection deleted successfully."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        query = """
        SELECT 
            userId as "userId", 
            username as "userName"
        FROM 
            UserApp
        WHERE 
            username = %s AND password_ = %s
        """
        params = (username, password)
        users = execute_query(query, params=params, cursor_factory=RealDictCursor)
        if not users:
            return jsonify({"error": "Invalid username or password."}), 401

        user = users[0]

        user_response = {
            "userId": user["userId"],
            "userName": user["userName"]
        }
        return jsonify(user_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        check_query = "SELECT userId FROM UserApp WHERE username = %s"
        check_params = (username,)
        existing_users = execute_query(check_query, params=check_params, cursor_factory=RealDictCursor)

        if existing_users:
            return jsonify({"error": "Username already exists."}), 409

        insert_query = """
        INSERT INTO UserApp (username, password_)
        VALUES (%s, %s)
        RETURNING userId as "userId", username as "userName"
        """
        insert_params = (username, password)
        new_user = execute_query(insert_query, params=insert_params, cursor_factory=RealDictCursor)

        if not new_user:
            return jsonify({"error": "Failed to create user."}), 500

        user = new_user[0]
        return jsonify(user), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/logout', methods=['POST'])
def logout():
    try:
        # TODO
        return jsonify({"message": "Logout successful."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
