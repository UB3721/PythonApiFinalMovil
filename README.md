Todo lo necesario para correr la api se encuentra en este repositorio
En ./Base se encuentra el script que crea la base, y los dos stored procedures utilizados. Se puede correr postgres y pgadmin utilizando el docker (Colocar postgres como red en la ui de pgadmin, o correr con cualquier instalación)

Para correr app.py simplemente instalar los requerimientos, ya sea en conda, .env o el método utilizado. Desarrollado en python 3.10.15

GET /userManga

    Recibe: Parámetros userId (obligatorio), mangaId (opcional).
    Devuelve: Información de mangas del usuario o un manga específico.

GET /userManga/favorites

    Recibe: Parámetro userId.
    Devuelve: Lista de mangas favoritos del usuario.

POST /userManga

    Recibe: JSON con información del usuario y manga.
    Devuelve: Mensaje de éxito al guardar.

PUT /userManga

    Recibe: JSON con información actualizada del usuario y manga.
    Devuelve: Mensaje de éxito al actualizar.

GET /allUsers

    Recibe: Parámetro userId.
    Devuelve: Lista de usuarios excepto el actual.

GET /user

    Recibe: Parámetro userId.
    Devuelve: Información del usuario.

POST /sharedLink

    Recibe: JSON con información del remitente, destinatario y manga.
    Devuelve: Mensaje de éxito al guardar.

GET /sharedLink

    Recibe: Parámetro userId.
    Devuelve: Lista de enlaces compartidos para el usuario.

PUT /sharedLink

    Recibe: JSON con información de la relación compartida.
    Devuelve: Mensaje de éxito al actualizar.

GET /user/statistics

    Recibe: Parámetro userId.
    Devuelve: Estadísticas de lectura del usuario.

POST /collection

    Recibe: JSON con userId y collectionName.
    Devuelve: Mensaje de éxito al crear colección.

GET /collection

    Recibe: Parámetro userId.
    Devuelve: Lista de colecciones del usuario.

GET /mangaCollection

    Recibe: Parámetros userId, collectionId.
    Devuelve: Mangas dentro de una colección específica.

GET /collection/<int:manga_id>/<int:user_id>

    Recibe: mangaId y userId.
    Devuelve: Colecciones relacionadas con un manga y usuario.

POST /mangaCollection

    Recibe: JSON con mangaId, userId, y collectionIdList.
    Devuelve: Mensaje de éxito al procesar las colecciones.

DELETE /mangaCollection

    Recibe: Parámetros userId, collectionId, mangaId.
    Devuelve: Mensaje de éxito al eliminar manga de la colección.

DELETE /userManga

    Recibe: Parámetros userId, mangaId.
    Devuelve: Mensaje de éxito al eliminar relación de usuario y manga.

DELETE /collection

    Recibe: Parámetros userId, collectionId.
    Devuelve: Mensaje de éxito al eliminar colección.

POST /users/login

    Recibe: JSON con username, password.
    Devuelve: Información del usuario si las credenciales son correctas.
    
    
POST /users/signup

    Recibe: JSON con username, password.
    Devuelve: Información del usuario creado.
