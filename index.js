import express from "express";
import { exec } from "child_process";
import cors from "cors";

const app = express();
app.use(cors());

app.get('/download', async (req, res) => {
  const url = req.query.url;
  if (!url) return res.json({ status: 'error', message: 'No URL provided' });

  console.log('Downloading:', url);
  // yt-dlp -g gives a direct URL for the best format
  exec(`yt-dlp -f best -g "${url}"`, (err, stdout, stderr) => {
    if (err || !stdout) {
      console.error(stderr || err);
      return res.json({ status: 'error', message: 'Download failed' });
    }
    const link = stdout.trim();
    res.json({ status: 'ok', url: link, platform: detectPlatform(url) });
  });
});

function detectPlatform(url) {
  url = url.toLowerCase();
  if (url.includes('tiktok')) return 'tiktok';
  if (url.includes('instagram')) return 'instagram';
  if (url.includes('youtube') || url.includes('youtu.be')) return 'youtube';
  if (url.includes('facebook') || url.includes('fb.watch')) return 'facebook';
  if (url.includes('twitter') || url.includes('x.com')) return 'twitter';
  if (url.includes('soundcloud')) return 'soundcloud';
  if (url.includes('snapchat')) return 'snapchat';
  return 'unknown';
}

app.listen(8080, () => console.log('✅ API running on port 8080'));
