using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using Emgu.CV;
using Emgu.CV.CvEnum;
using Emgu.CV.Structure;
using Newtonsoft.Json;
using System.IO; 

public static class MinimapDetector
{
    // Red color thresholds
    private static readonly ScalarArray lowerRed = new ScalarArray(new MCvScalar(100, 0, 0));
    private static readonly ScalarArray upperRed = new ScalarArray(new MCvScalar(255, 100, 100));
   static void Main(String[] args)
    {
        Console.WriteLine("HEllo WOrld "); 
    }
    public static string CaptureAndDetect(Dictionary<String, int> cords, Dictionary<string, Mat> championImages)
    {
        Rectangle minimapArea = new Rectangle(cords["x"], cords["y"], cords["width"], cords["height"]);
        // List to store detected champions
        var detectedChampions = new List<ChampionData>();
        // Capture minimap
        using (var bitmap = new Bitmap(minimapArea.Width, minimapArea.Height))
        {
            using (var graphics = Graphics.FromImage(bitmap))
            {
                graphics.CopyFromScreen(minimapArea.Location, Point.Empty, minimapArea.Size);
            }

            // Convert Bitmap to Mat
            var frame = BitmapToMat(bitmap);

            // Create mask for red areas (representing champions)
            var maskRed = new Mat();
            CvInvoke.InRange(frame, lowerRed, upperRed, maskRed);

            // Apply GaussianBlur to reduce noise
            CvInvoke.GaussianBlur(maskRed, maskRed, new Size(3, 3), 2);

            // Detect circles using Hough Circle Transformation
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

            if (circles.Length > 0)
            {
                foreach (var circle in circles)
                {
                    // Extract circle region from the frame
                    Rectangle circleRect = new Rectangle(
                        (int)(circle.Center.X - circle.Radius),
                        (int)(circle.Center.Y - circle.Radius),
                        (int)(2 * circle.Radius),
                        (int)(2 * circle.Radius)
                    );

                    if (circleRect.X >= 0 && circleRect.Y >= 0 &&
                        circleRect.Right <= frame.Width && circleRect.Bottom <= frame.Height)
                    {
                        Mat circleImg = new Mat(frame, circleRect);

                        // Match the circle image against known champions
                        string detectedChampion = FindBestMatch(circleImg, championImages);

                        if (detectedChampion != null)
                        {
                            // Add detected champion and its position to the list
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
        }

        // Serialize detected champions to JSON
        return JsonConvert.SerializeObject(detectedChampions);
    }

    private static string FindBestMatch(Mat circleImg, Dictionary<string, Mat> championImages)
    {
        string bestMatch = null;
        double highestScore = 0.2; // Similarity threshold

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
