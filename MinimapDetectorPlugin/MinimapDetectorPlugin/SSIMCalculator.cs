using Emgu.CV;
using Emgu.CV.CvEnum;
using Emgu.CV.Structure;

public static class SSIMCalculator
{
    public static double CalculateSSIM(Mat img1, Mat img2)
    {
        CvInvoke.CvtColor(img1, img1, ColorConversion.Bgr2Gray);
        CvInvoke.CvtColor(img2, img2, ColorConversion.Bgr2Gray);

        CvInvoke.Resize(img2, img2, img1.Size);

        var result = new Mat();
        CvInvoke.MatchTemplate(img1, img2, result, TemplateMatchingType.CcoeffNormed);
        
        var data = result.GetData() as float[,];
        double maxValue = 0;

        if (data != null)
        {
            foreach (var value in data)
            {
                if (value > maxValue) maxValue = value;
            }
        }

        return maxValue;

    }
}