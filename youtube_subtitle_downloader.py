import yt_dlp 
import os 
import ssl 

# 禁用SSL验证以避免证书错误 
ssl._create_default_https_context = ssl._create_unverified_context 

def convert_srt_to_txt(srt_file_path): 
    """将SRT格式字幕转换为纯文本格式"""
    try: 
        with open(srt_file_path, 'r', encoding='utf-8') as f: 
            srt_content = f.read() 
        
        # 移除SRT格式标记（序号、时间戳）
        lines = srt_content.split('\n') 
        txt_lines = [] 
        
        for line in lines: 
            # 跳过序号行
            if line.strip().isdigit(): 
                continue 
            # 跳过时间戳行
            elif '-->' in line: 
                continue 
            # 跳过空行
            elif not line.strip(): 
                continue 
            # 添加字幕文本行
            else: 
                txt_lines.append(line.strip()) 
        
        # 创建txt文件路径
        txt_file_path = srt_file_path.replace('.srt', '.txt') 
        
        # 写入txt文件
        with open(txt_file_path, 'w', encoding='utf-8') as f: 
            f.write('\n'.join(txt_lines)) 
        
        print(f"已将SRT转换为TXT格式: {txt_file_path}") 
        return txt_file_path 
    except Exception as e: 
        print(f"转换SRT到TXT时出错: {e}") 
        return None 

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
            
            # 确保最终有txt文件
            txt_file = None
            
            # 首先检查是否已有txt文件
            for file in subtitle_files:
                if file.endswith('.txt') and not ('detailed_guide' in file or 'manual' in file or 'error' in file):
                    # 检查内容是否为干净的文本
                    try:
                        with open(f'subtitles/{file}', 'r', encoding='utf-8') as f:
                            content = f.read()
                        if not ('<html>' in content.lower() or '<body>' in content.lower()) and '-->' not in content:
                            txt_file = file
                            print(f"找到已存在的干净txt文件: {txt_file}")
                            break
                    except:
                        continue
            
            # 如果没有合适的txt文件，尝试转换srt
            if not txt_file:
                srt_file = None
                for file in subtitle_files:
                    if file.endswith('.srt'):
                        srt_file = file
                        break
                
                if srt_file:
                    converted_txt = convert_srt_to_txt(f'subtitles/{srt_file}')
                    if converted_txt:
                        txt_file = os.path.basename(converted_txt)
                        print(f"已转换并选择txt文件: {txt_file}")
            
            # 如果还是没有txt文件，尝试从其他格式创建
            if not txt_file:
                # 找一个非HTML的文件
                source_file = None
                for file in subtitle_files:
                    try:
                        with open(f'subtitles/{file}', 'r', encoding='utf-8') as f:
                            content = f.read()
                        if not ('<html>' in content.lower() or '<body>' in content.lower()):
                            source_file = file
                            break
                    except:
                        continue
                
                if source_file:
                    # 读取内容并创建txt文件
                    try:
                        with open(f'subtitles/{source_file}', 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 清理内容
                        if '-->' in content:  # 如果是srt或vtt格式
                            lines = content.split('\n')
                            clean_lines = []
                            for line in lines:
                                if line.strip().isdigit() or '-->' in line or not line.strip():
                                    continue
                                clean_lines.append(line.strip())
                            content = '\n'.join(clean_lines)
                        
                        # 创建txt文件
                        txt_file_path = f'subtitles/{video_id}.txt'
                        with open(txt_file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        txt_file = os.path.basename(txt_file_path)
                        print(f"已从{source_file}创建txt文件: {txt_file}")
                    except Exception as e:
                        print(f"创建txt文件时出错: {e}")
            
            # 如果最终还是没有txt文件，使用第一个文件
            if not txt_file and subtitle_files:
                txt_file = subtitle_files[0]
                print(f"警告：无法创建txt文件，使用原始文件: {txt_file}")
            
            # 读取最终文件
            if txt_file:
                try:
                    with open(f'subtitles/{txt_file}', 'r', encoding='utf-8') as f:
                        subtitle_content = f.read()
                    
                    # 再次清理内容，确保是干净的txt
                    if '-->' in subtitle_content or subtitle_content.strip().isdigit():
                        lines = subtitle_content.split('\n')
                        clean_lines = []
                        for line in lines:
                            if line.strip().isdigit() or '-->' in line or not line.strip():
                                continue
                            clean_lines.append(line.strip())
                        subtitle_content = '\n'.join(clean_lines)
                        
                        # 保存清理后的内容
                        clean_txt_path = f'subtitles/{video_id}.clean.txt'
                        with open(clean_txt_path, 'w', encoding='utf-8') as f:
                            f.write(subtitle_content)
                        txt_file = os.path.basename(clean_txt_path)
                        print(f"已清理并保存为干净的txt文件: {txt_file}")
                    
                    return subtitle_content, txt_file
                except Exception as e:
                    print(f"读取文件时出错: {e}")
                    return None, None
            else:
                print("未找到或无法创建字幕文件")
                return None, None
        else: 
            print("未找到生成的字幕文件") 
            return None, None 
    except Exception as e: 
        print(f"下载字幕时出错: {e}") 
        return None, None 

def main(): 
    # 获取用户输入的视频链接 
    video_url = input("请输入YouTube视频链接: ").strip() 
    
    if not video_url:
        print("错误：视频链接不能为空")
        return
    
    print(f"\n开始下载视频字幕: {video_url}") 
    print(f"{'='*80}") 
    
    # 下载字幕 
    subtitle, filename = download_subtitle(video_url) 
    
    if subtitle: 
        print(f"\n{'='*80}") 
        print(f"字幕处理完成!") 
        print(f"最终txt文件: {filename}") 
        print(f"文件路径: subtitles/{filename}") 
        print(f"{'='*80}") 
        
        # 显示字幕内容预览 
        print("\n字幕内容预览:") 
        lines = subtitle.split('\n') 
        preview_lines = lines[:20]  # 显示前20行 
        print('\n'.join(preview_lines)) 
        if len(lines) > 20: 
            print("...") 
        
        # 确认输出
        print(f"\n{'='*80}") 
        print("✅ 任务完成！您已获得干净的txt字幕文件") 
        print(f"文件位置: subtitles/{filename}") 
        print(f"{'='*80}") 
    else: 
        print(f"\n{'='*80}") 
        print(f"字幕处理失败") 
        print(f"{'='*80}") 

if __name__ == "__main__": 
    main()