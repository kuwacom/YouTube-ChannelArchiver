import yt_dlp
import os
import json

# ダウンロードする動画の関数
def downloadVideo(url, saveDir):
    # yt-dlpオプション
    ydlOpts = {
        'outtmpl': os.path.join(saveDir, '%(title)s.%(ext)s'),  # 保存先のテンプレート
        'writeinfojson': True,  # メタデータをJSONで保存
        'quiet': False,  # ログ表示
        # 'progress_hooks': [progressHook],  # プログレスフック
        # 'force_generic_extractor': True,  # 強制的にジェネリックエクストラクターを使う
    }

    # yt-dlpのインスタンス作成
    with yt_dlp.YoutubeDL(ydlOpts) as ydl:
        ydl.download([url])

# プログレスフックで進行状況を更新
# 動画保存完了後に現在のprogressを保存
def progressHook(progressData):    
    global downloadedVideos
    global progressFile

    if progressData['status'] == 'finished':
        videoId = progressData['info_dict']['id']
        # videoTitle = progressData['info_dict']['title']
        # videoFilename = progressData['filename']
        
        # 動画情報を保存
        downloadedVideos.append(videoId)
        # 進行状況の保存
        with open(progressFile, 'w') as f:
            json.dump(downloadedVideos, f)

# チャンネルのメタ情報からすべての動画URLを取得
def getChannelVideos(channelMeta):
    return [entry['url'] for entry in channelMeta['entries'][0]['entries']]

# チャンネルのメタ情報を取得
def getChannelMeta(channelUrl):
    ydlOpts = {
        'quiet': True,
        'extract_flat': True,  # url_resultsをさらに解決および処理
    }
    with yt_dlp.YoutubeDL(ydlOpts) as ydl:
        return ydl.extract_info(channelUrl, download=False)

def main():
    global downloadedVideos
    global progressFile

    # チャンネルのURL
    channelUrl = input("チャンネルURLを入力してください: ")

    channelMeta = getChannelMeta(channelUrl)

    # 保存先ディレクトリ
    saveDir = channelMeta['uploader_id']
    # 再開用の進行状況を保存するファイル
    progressFile = saveDir + '/downloadProgress.json'
    channelMetaFile = saveDir + '/channelMeta.json'

    # 保存先ディレクトリの作成
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # チャンネルのメタ情報を保存
    with open(channelMetaFile, 'w') as f:
        json.dump(channelMeta, f)

    # 進行状況の読み込み
    if os.path.exists(progressFile):
        with open(progressFile, 'r') as f:
            downloadedVideos = json.load(f)

    videoUrls = getChannelVideos(channelMeta)

    for url in videoUrls:
        videoId = url.split('v=')[-1]
        if videoId not in downloadedVideos:
            print(f"Downloading video: {url}")
            downloadVideo(url, saveDir)
        else:
            print(f"Skipping already downloaded video: {url}")

    print("All videos processed.")

if __name__ == "__main__":
    # 進行状況管理用list
    downloadedVideos = []
    progressFile = ""
    main()
