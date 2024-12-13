using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using Emgu.CV;
using Emgu.CV.CvEnum;
using Emgu.CV.Structure;
using Newtonsoft.Json;
using System.IO;

public class MinimapDetector
{
    private static readonly ScalarArray LowerRed = new ScalarArray(new MCvScalar(100, 0, 0));
    private static readonly ScalarArray UpperRed = new ScalarArray(new MCvScalar(255, 100, 100));

    public string CaptureAndDetect(int x, int y, int width, int height, List<string> championNames)
    {
        Dictionary<string, Mat> championImages = LoadChampionImages(championNames);
        Rectangle minimapArea = new Rectangle(x, y, width, height);
        var detectedChampions = new List<ChampionData>();

        using (var bitmap = new Bitmap(minimapArea.Width, minimapArea.Height))
        {
            using (var graphics = Graphics.FromImage(bitmap))
            {
                graphics.CopyFromScreen(minimapArea.Location, Point.Empty, minimapArea.Size);
            }

            var frame = BitmapToMat(bitmap);

            var maskRed = new Mat();
            CvInvoke.InRange(frame, LowerRed, UpperRed, maskRed);
            CvInvoke.GaussianBlur(maskRed, maskRed, new Size(3, 3), 2);

            CircleF[] circles = CvInvoke.HoughCircles(
                maskRed,
                HoughModes.Gradient,
                dp: 1.2,
                minDist: 20,
                param1: 50,
                param2: 30,
                minRadius: 8,
                maxRadius: 20
            );

            foreach (var circle in circles)
            {
                var circleRect = new Rectangle(
                    (int)(circle.Center.X - circle.Radius),
                    (int)(circle.Center.Y - circle.Radius),
                    (int)(2 * circle.Radius),
                    (int)(2 * circle.Radius)
                );

                if (IsValidRectangle(circleRect, frame))
                {
                    Mat circleImg = new Mat(frame, circleRect);
                    string detectedChampion = FindBestMatch(circleImg, championImages);

                    if (!string.IsNullOrEmpty(detectedChampion))
                    {
                        detectedChampions.Add(new ChampionData
                        {
                            Name = detectedChampion,
                            X = (int)circle.Center.X,
                            Y = (int)circle.Center.Y
                        });
                    }
                }
            }
        }
        return JsonConvert.SerializeObject(detectedChampions);
    }

    private static Dictionary<string, Mat> LoadChampionImages(List<string> championNames)
    {
        var championImages = new Dictionary<string, Mat>();
        string basePath = "champion_images";

        foreach (string champName in championNames)
        {
            string filePath = Path.Combine(basePath, champName + ".png");
            if (File.Exists(filePath))
            {
                Mat champImg = CvInvoke.Imread(filePath, ImreadModes.Color);
                if (champImg != null)
                {
                    championImages[champName] = champImg;
                }
            }
        }
        return championImages;
    }

    private static bool IsValidRectangle(Rectangle rect, Mat frame)
    {
        return rect.X >= 0 && rect.Y >= 0 && rect.Right <= frame.Width && rect.Bottom <= frame.Height;
    }

    private static string FindBestMatch(Mat circleImg, Dictionary<string, Mat> championImages)
    {
        string bestMatch = null;
        double highestScore = 0.2;

        foreach (var champ in championImages)
        {
            Mat resizedChampion = champ.Value.Clone();
            CvInvoke.Resize(resizedChampion, resizedChampion, new Size(circleImg.Width, circleImg.Height));

            double score = SSIMCalculator.CalculateSSIM(circleImg, resizedChampion);

            if (score > highestScore)
            {
                highestScore = score;
                bestMatch = champ.Key;
            }
        }
        return bestMatch;
    }

    private static Mat BitmapToMat(Bitmap bitmap)
    {
        Mat mat = new Mat(bitmap.Height, bitmap.Width, DepthType.Cv8U, 3);
        BitmapData bitmapData = bitmap.LockBits(
            new Rectangle(0, 0, bitmap.Width, bitmap.Height),
            ImageLockMode.ReadOnly,
            PixelFormat.Format24bppRgb
        );

        CvInvoke.CvtColor(
            new Mat(bitmapData.Height, bitmapData.Width, DepthType.Cv8U, 3, bitmapData.Scan0, bitmapData.Stride),
            mat,
            ColorConversion.Bgr2Rgb
        );

        bitmap.UnlockBits(bitmapData);
        return mat;
    }
}

public class ChampionData
{
    public string Name { get; set; }
    public int X { get; set; }
    public int Y { get; set; }
}
