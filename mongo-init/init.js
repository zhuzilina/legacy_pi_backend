// MongoDB初始化脚本
// 创建md_docs数据库和用户

// 切换到md_docs数据库
db = db.getSiblingDB('md_docs');

// 创建应用用户
db.createUser({
  user: 'md_docs_user',
  pwd: 'md_docs_password',
  roles: [
    {
      role: 'readWrite',
      db: 'md_docs'
    }
  ]
});

// 创建集合
db.createCollection('documents');
db.createCollection('images');
db.createCollection('categories');

// 创建索引
db.documents.createIndex({ "category": 1 });
db.documents.createIndex({ "is_published": 1 });
db.documents.createIndex({ "created_at": -1 });
db.documents.createIndex({ "title": "text", "content": "text" });

db.images.createIndex({ "document_id": 1 });
db.images.createIndex({ "upload_time": -1 });

db.categories.createIndex({ "code": 1 }, { unique: true });
db.categories.createIndex({ "sort_order": 1 });

print('MongoDB初始化完成');
