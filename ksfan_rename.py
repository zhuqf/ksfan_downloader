import requests, urllib, re, logging, io, os

class pyksfan:
    site_url = 'https://ksfan.net/story/'
    audio_url = 'https://ksfan.net{}'
    page_url = 'https://ksfan.net/story/{}/?page={}'
    target_file = '{}/{}/{} {}.mp3'
    rename_file = '{}/{}/{:3d} {}.mp3'
    newname_file = '{}/{}/{:03d} {}.mp3'

    out = None

    def __init__(self, story, maxpage, targetDir):
        self.session = requests.Session() 
        self.story = story 
        self.maxpage = maxpage 
        self.targetDir = targetDir
    
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger('pyksfan')
        self.logger.setLevel(logging.INFO)

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.cookies.clear()
        if self.out is not None:
            self.out.close()
   
    def getTitleFromWeb(content):
#        keyword = 'meta name="description" content="([^ ]*) - (.*)">'
        keyword = '<h5>(.*)</h5>'
        match = re.search(keyword, content)
        if match:
            return match.group(1)
        return None

    def getAudioFromWeb(content):
        expr = 'var audio = new Audio\(\'(.*)\'\)'
        match = re.search(expr, content)
        if match:
            return match.group(1)
        return None
            
 
    def getStoryPage(self, pagenum):
        story_page_url = pyksfan.page_url.format( self.story, pagenum )
        try:
            resp = self.session.get(story_page_url)
            if resp.status_code == 200:
                return resp.text
            else:
                self.logger.warning("can not find the story page %d error", resp.status_code)
        except requests.exceptions.ConnectionError:
            self.logger.warning("requests.exceptions.ConnectionError")
        except requests.exceptions.TooManyRedirects:
            self.logger.warning("except requests.exceptions.TooManyRedirects")
        except:
            self.logger.warning("Network Error!")
        return None


    def getStoryInfo(self, pagenum):
        content = self.getStoryPage(pagenum);
        title = pyksfan.getTitleFromWeb(content)
        audio = pyksfan.getAudioFromWeb(content)
        return title, audio

    def downloadStory(self, pagenum, title, audio):
        story_page_url = pyksfan.page_url.format( self.story, pagenum )
        headers={ 'Host': 'ksfan.net', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0', 'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Referer': story_page_url }

        self.logger.debug(headers)
        url = pyksfan.audio_url.format(audio)
        self.logger.debug(url)
        try:
            mp3 = self.session.get(url, headers=headers)
            if mp3.status_code == 200:
                target_file = pyksfan.target_file.format(self.targetDir, self.story, pagenum, title)
                self.logger.debug(target_file)
                with io.open( target_file, mode='wb') as afile:
                    afile.write(mp3.content)
                return mp3.status_code
            else:
                self.logger.warning("can not find the story page %d error", resp.status_code)
        except requests.exceptions.ConnectionError:
            self.logger.warning("requests.exceptions.ConnectionError")
        except requests.exceptions.TooManyRedirects:
            self.logger.warning("except requests.exceptions.TooManyRedirects")
        except:
            self.logger.warning("Network Error!")



    def download(self):
        for i in range(1, self.maxpage):
            title, audio = self.getStoryInfo(i)
            target_file = pyksfan.target_file.format(self.targetDir, self.story, i, title)
            if os.path.isfile(target_file) is not True:
                self.downloadStory(i, title, audio)

    def rename(self):
        for i in range(1, self.maxpage):
            title, audio = self.getStoryInfo(i)
            rename_file = pyksfan.rename_file.format(self.targetDir, self.story, i, title)
            self.logger.info(rename_file)
            if os.path.isfile(rename_file) is True:
                newname_file = pyksfan.newname_file.format(self.targetDir, self.story, i, title)
                self.logger.info(newname_file)
                os.rename(rename_file, newname_file)

if __name__ == "__main__":
    ksfan = pyksfan('kai-shu-san-guo-yan-yi', 372, '/Users/zhuqf/Music')
    ksfan.rename()
