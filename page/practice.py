import requests
import time


def get_kugou_song_info(hash_id):
    """获取歌曲信息（兼容API变动）"""
    api_urls = [
        f"http://www.kugou.com/yy/index.php?r=play/getdata&hash={hash_id}",
        f"https://m3ws.kugou.com/api/v1/song/get_song_info?hash={hash_id}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": "kg_mid=123456"  # 替换为你的Cookie
    }

    for url in api_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10).json()
            if response.get("data"):
                return response["data"]
            print(f"API返回异常: {response.get('error')}")
        except Exception as e:
            print(f"请求失败: {e}")
        time.sleep(1)
    return None


def download_song(song_name):
    """从歌曲名到下载全流程"""
    hash_id = get_kugou_hash(song_name)  # 复用之前的搜索函数
    if not hash_id:
        print("无法获取 hash！")
        return

    song_data = get_kugou_song_info(hash_id)
    if not song_data:
        print("无法获取歌曲信息！")
        return

    if song_data.get("is_vip") == 1:
        print("VIP歌曲，无法下载！")
        return

    mp3_url = song_data.get("play_url")
    if not mp3_url:
        print("未找到下载链接！")
        return

    # 下载文件
    song_name = song_data["audio_name"].replace("/", "_")
    with open(f"{song_name}.mp3", "wb") as f:
        f.write(requests.get(mp3_url).content)
    print(f"下载完成: {song_name}.mp3")

def get_kugou_hash(song_name):
    """获取歌曲 hash（带重试机制）"""
    search_url = "https://songsearch.kugou.com/song_search_v2"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": "kg_mid=123456; kg_dfid=abc..."  # 替换为你的Cookie
    }
    for _ in range(3):  # 重试3次
        try:
            response = requests.get(
                search_url,
                params={"keyword": song_name, "page": 1, "pagesize": 1},
                headers=headers,
                timeout=5
            ).json()
            if response["data"]["lists"]:
                return response["data"]["lists"][0]["FileHash"]
            print("未找到歌曲！")
            return None
        except Exception as e:
            print(f"搜索失败: {e}")
            time.sleep(2)
    return None
# 使用示例
download_song("周杰伦 晴天")