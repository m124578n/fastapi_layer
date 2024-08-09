db = db.getSiblingDB("");

db.createUser({
    user: "",
    pwd: "",
    roles: [
        {
            role: 'readWrite',
            db: ''
        },
    ],
});

db.createCollection("user");
db.createCollection("contest");