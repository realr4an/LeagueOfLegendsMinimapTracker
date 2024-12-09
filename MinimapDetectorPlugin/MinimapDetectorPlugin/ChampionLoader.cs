using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using Emgu.CV;

public static class ChampionLoader
{
    public static Dictionary<string, Mat> LoadChampionImages(string path)
    {
        var championImages = new Dictionary<string, Mat>();
        foreach (var file in Directory.GetFiles(path, "*.png"))
        {
            var champName = Path.GetFileNameWithoutExtension(file);
            var champImage = CvInvoke.Imread(file, Emgu.CV.CvEnum.ImreadModes.Color);
            if (champImage != null)
            {
                championImages[champName] = champImage;
            }
        }
        return championImages;
    }
}