import requests

def download_url():
    # 输入URL并自动补全协议
    url = input("Please input a URL: ").strip()
    # https://rtxie.github.io/
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # 默认添加HTTP协议

    try:
        # 发送HTTP GET请求，设置超时时间为5秒
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 检查HTTP状态码（非200会抛出异常）

        # 生成文件名：去除协议，替换特殊字符
        filename = url.split('//')[-1].replace('/', '_').replace(':', '') + '.html'
        
        # 保存网页内容（文本模式）
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # 计算文件大小（二进制内容长度）
        file_size = len(response.content)
        
        # 输出结果
        print(f"The requested URL: {response.url}") 
        print(f"The saved file: {filename}")
        print(f"The requested file size: {file_size} bytes")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_url()