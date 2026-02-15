import yt_dlp
import os
import ssl

# 禁用SSL验证以避免证书错误
ssl._create_default_https_context = ssl._create_unverified_context

def download_subtitle(video_url):
    try:
        print(f"正在获取视频信息: {video_url}")
        
        # 提取视频ID
        video_id = video_url.split('v=')[1].split('&')[0] if 'v=' in video_url else video_url
        print(f"视频ID: {video_id}")
        
        # 确保subtitles目录存在
        if not os.path.exists('subtitles'):
            os.makedirs('subtitles')
        
        # 配置yt-dlp
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,  # 启用自动生成字幕
            'subtitlesformat': 'srt',
            'subtitleslangs': ['en', 'en-US'],
            'skip_download': True,
            'outtmpl': f'subtitles/{video_id}',
            'no_warnings': True,
            'quiet': False,
            'timeout': 60,  # 增加超时时间到60秒
            'ignoreerrors': True,  # 忽略错误
            'nocheckcertificate': True,  # 禁用证书检查
        }
        
        # 使用yt-dlp下载字幕
        print("正在配置yt-dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("正在提取视频信息...")
            info = ydl.extract_info(video_url, download=False)
            print(f"视频标题: {info.get('title', '未知')}")
            print(f"可用字幕: {info.get('subtitles', {})}")
            print(f"自动生成字幕: {info.get('automatic_captions', {})}")
            
            # 下载字幕
            print("正在下载字幕...")
            ydl.download([video_url])
        
        print("字幕已成功下载")
        
        # 查找生成的字幕文件
        subtitle_files = []
        for file in os.listdir('subtitles'):
            if video_id in file and (file.endswith('.srt') or file.endswith('.vtt') or file.endswith('.txt')):
                subtitle_files.append(file)
        
        if subtitle_files:
            print(f"生成的字幕文件: {subtitle_files}")
            # 读取第一个字幕文件的内容
            with open(f'subtitles/{subtitle_files[0]}', 'r', encoding='utf-8') as f:
                subtitle_content = f.read()
            return subtitle_content, subtitle_files[0]
        else:
            print("未找到生成的字幕文件")
            return None, None
            
    except Exception as e:
        print(f"下载字幕时出错: {e}")
        return None, None

def main():
    # 用户提供的视频链接
    video_url = "https://www.youtube.com/watch?v=4VSUrwbd0Jw"
    
    print(f"开始下载视频字幕: {video_url}")
    
    # 下载字幕
    subtitle, filename = download_subtitle(video_url)
    
    if subtitle:
        print(f"\n{'='*80}")
        print(f"字幕下载完成!")
        print(f"字幕文件: {filename}")
        print(f"{'='*80}")
        
        # 显示字幕内容
        print("\n字幕内容预览:")
        lines = subtitle.split('\n')
        preview_lines = lines[:20]  # 显示前20行
        print('\n'.join(preview_lines))
        if len(lines) > 20:
            print("...")
    else:
        print(f"\n{'='*80}")
        print(f"字幕下载失败")
        print(f"{'='*80}")

if __name__ == "__main__":
    main()