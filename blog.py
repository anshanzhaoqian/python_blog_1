import os
import pymysql
from jinja2 import Environment, FileSystemLoader

# --- 1. 配置参数 ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password', # 替换为你的密码
    'database': 'blog_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # 返回字典格式，方便模板调用
}

OUTPUT_DIR = 'dist'
TEMPLATE_DIR = 'templates'

def fetch_posts_from_db():
    """从数据库中读取所有博客文章"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, title, content, summary, created_at FROM posts ORDER BY created_at DESC"
            cursor.execute(sql)
            posts = cursor.fetchall()
            # 格式化时间为字符串，避免 Jinja2 渲染报错
            for post in posts:
                if post['created_at']:
                    post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            return posts
    finally:
        connection.close()

def main():
    # 确保输出目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # --- 2. 初始化 Jinja2 模板环境 ---
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    index_template = env.get_template('index.html')
    detail_template = env.get_template('detail.html')

    # --- 3. 获取数据 ---
    print("正在从 MySQL 读取文章数据...")
    posts = fetch_posts_from_db()
    if not posts:
        print("未找到任何文章，请先在数据库中插入数据。")
        return

    # --- 4. 生成文章详情页 (detail.html) ---
    print(f"开始生成详情页，共 {len(posts)} 篇...")
    for post in posts:
        # 为每篇文章定义一个独立的文件名，如 dist/post_1.html
        file_name = f"post_{post['id']}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        
        # 渲染单篇文章
        html_content = detail_template.render(post=post)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f" 已生成详情页: {file_path}")

    # --- 5. 生成博客首页 (index.html) ---
    print("开始生成首页...")
    index_html_content = index_template.render(posts=posts)
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html_content)
    print(f" 成功生成首页: {index_path}")
    
    print("\n静态网站生成完毕！请查看 'dist/' 文件夹。")

if __name__ == '__main__':
    main()
