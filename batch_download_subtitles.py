import yt_dlp
import os
import ssl

# 禁用SSL验证以避免证书错误
ssl._create_default_https_context = ssl._create_unverified_context

def download_subtitle(video_url):
    try:
        print(f"\n{'='*80}")
        print(f"正在处理: {video_url}")
        print(f"{'='*80}")
        
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
            
            # 下载字幕
            print("正在下载字幕...")
            ydl.download([video_url])
        
        print("字幕已成功下载")
        
        # 查找生成的字幕文件
        subtitle_files = []
        for file in os.listdir('subtitles'):
            if video_id in file and file.endswith('.srt'):
                subtitle_files.append(file)
        
        if subtitle_files:
            print(f"生成的字幕文件: {subtitle_files}")
            
            # 将srt格式转换为txt格式
            for srt_file in subtitle_files:
                txt_file = srt_file.replace('.srt', '.txt')
                srt_path = os.path.join('subtitles', srt_file)
                txt_path = os.path.join('subtitles', txt_file)
                
                # 读取srt文件并转换为txt
                with open(srt_path, 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                
                # 提取字幕文本，去除时间戳和序号
                lines = srt_content.split('\n')
                txt_lines = []
                for line in lines:
                    # 跳过空行、序号和时间戳
                    if not line.strip():
                        continue
                    if line.strip().isdigit():
                        continue
                    if '--> ' in line:
                        continue
                    txt_lines.append(line)
                
                # 保存为txt文件
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(txt_lines))
                
                print(f"已转换为txt格式: {txt_file}")
            
            return True
        else:
            print("未找到生成的字幕文件")
            return False
            
    except Exception as e:
        print(f"下载字幕时出错: {e}")
        return False

def main():
    # 从文件中读取视频链接
    links_file = 'video_links.txt'
    
    if not os.path.exists(links_file):
        print(f"错误: {links_file} 文件不存在")
        print("请创建一个名为 video_links.txt 的文件，并在其中逐行写入视频链接")
        return
    
    # 读取视频链接
    with open(links_file, 'r', encoding='utf-8') as f:
        video_links = [line.strip() for line in f if line.strip()]
    
    print(f"总共找到 {len(video_links)} 个视频链接")
    print(f"开始批量下载字幕...")
    
    # 处理所有视频链接
    success_count = 0
    fail_count = 0
    
    for i, video_url in enumerate(video_links, 1):
        print(f"\n处理第 {i} 个链接:")
        if download_subtitle(video_url):
            success_count += 1
        else:
            fail_count += 1
    
    # 显示结果
    print(f"\n{'='*80}")
    print(f"批量处理完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"总处理: {success_count + fail_count}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()