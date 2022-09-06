/****************************************************
    文件：GameControl.cs
    作者：XINWEI DUAN
    邮箱: 2650178d@student.gla.ac.uk
    日期：#CreateGameCenter#
    功能：Control the logic of game
*****************************************************/

using System.Collections.Generic;
using System.Xml;
using UnityEngine;
using System.Text.RegularExpressions;
public class GameControl : MonoBehaviour 
{
    public static GameControl Instance;
    public float MapSizeX = 8.0f;
    public float MapSizeY = 5.0f;


    private void Awake()
    {
        Instance = this;
        InitMapComData(PathDefine.MapComCfg);
        InitAnimalData(PathDefine.AnimalComCfg);
    }

    private void Start()
    {
        MapControl.Instance.Init(MapCfgArr, AnimalCfgArr);
    }
    //将识别到的地图组件和动物信息的xml转化为list形式
    #region InitMapCfg
    //存放识别的场景中组件信息
    public List<MapComData> MapCfgArr = new List<MapComData>();

    public void InitMapComData(string path)
    {
        //获取xml文件
        TextAsset xml = Resources.Load<TextAsset>(path);
        if (!xml)
        {
            Debug.LogError("地图组件信息不存在");
        }
        else
        {
            //建立xml文档，并从xml中读取内容
            XmlDocument doc = new XmlDocument();
            doc.LoadXml(xml.text);
            //将文档内容转化为一个节点列表
            XmlNodeList nodLst = doc.SelectSingleNode("root").ChildNodes;

            //遍历每个节点
            //如果当前节点的ID等于null,则代表遍历结束
            for (int i = 0; i < nodLst.Count; i++)
            {
                XmlElement ele = nodLst[i] as XmlElement;

                if (ele.GetAttributeNode("ID") == null)
                {
                    continue;
                }

                MapComData mc = new MapComData();

                foreach (XmlElement e in nodLst[i].ChildNodes)
                {
                    switch (e.Name)
                    {
                        case "CompName":
                            mc.ComName= e.InnerText;
                            break;
                        case "DetectionPos":
                            string[] valarr = Regex.Split(e.InnerText, "\\s+", RegexOptions.IgnoreCase);
                            if (valarr[0] == "[")
                            {
                                valarr[2] = valarr[2].Substring(0, valarr[2].Length - 1);
                                Vector3 varVec = new Vector3(float.Parse(valarr[1]), float.Parse(valarr[2]), 0);
                                mc.ComPos = varVec;
                                break;
                            }
                            else
                            {
                                valarr[0] = valarr[0].Substring(1);
                                valarr[1] = valarr[1].Substring(0, valarr[1].Length - 1);
                                Vector3 varVec = new Vector3(float.Parse(valarr[0]), float.Parse(valarr[1]), 0);
                                mc.ComPos = varVec;
                                break;
                            }
                        case "ImageSize":
                            string[] isarr = e.InnerText.Split();
                            isarr[0] = isarr[0].Substring(1, isarr[0].Length - 2);
                            isarr[1] = isarr[1].Substring(0, isarr[1].Length - 1);
                            if(mc.width==0)
                                mc.width = float.Parse(isarr[1]);
                            float pox = (mc.ComPos.x * 100 / (float.Parse(isarr[1]) / 2)) - 100;
                            float poy = 100-(mc.ComPos.y * 100 / (float.Parse(isarr[0])/2));
                            mc.ComPos = new Vector3((float)(pox*0.01 * MapSizeX),(float) (poy*0.01 * MapSizeY), 0);
                            if (mc.ComName.Equals("house") || mc.ComName.Equals("fence"))
                            {
                                mc.ComPos = new Vector3(mc.ComPos.x, mc.ComPos.y - 1f, 0);
                            }
                            else if (mc.ComName.Equals("tree"))
                            {
                                mc.ComPos = new Vector3(mc.ComPos.x, mc.ComPos.y - 0.56f, 0);
                            }
                            break;
                        case "FenceWidth":
                            if (mc.width != 0)
                            {
                                float fencearea = float.Parse(e.InnerText) / mc.width;
                                if (fencearea<0.60 && fencearea >= 0.35)
                                {
                                    MapComData mc2 = new MapComData();
                                    mc2.ComName = mc.ComName;
                                    //栅栏屏幕左边
                                    if (mc.ComPos.x <= 0)
                                    {
                                        mc2.ComPos = new Vector3(mc.ComPos.x + 3.36f, mc.ComPos.y, 0);
                                    }
                                    else
                                    {
                                        mc2.ComPos = new Vector3(mc.ComPos.x - 3.36f, mc.ComPos.y, 0);
                                    }
                                    MapCfgArr.Add(mc2);

                                }
                                else if(fencearea<=0.85 && fencearea >= 0.60)
                                {
                                    MapComData mc2 = new MapComData();
                                    mc2.ComName = mc.ComName;
                                    mc2.ComPos= new Vector3(mc.ComPos.x + 3.36f, mc.ComPos.y, 0);
                                    MapComData mc3 = new MapComData();
                                    mc3.ComName = mc.ComName;
                                    mc3.ComPos= new Vector3(mc.ComPos.x - 3.36f, mc.ComPos.y, 0);
                                    MapCfgArr.Add(mc2);
                                    MapCfgArr.Add(mc3);
                                }
                                else if (fencearea > 0.85)
                                {
                                    MapComData mc2 = new MapComData() { ComName = mc.ComName };
                                    MapComData mc3 = new MapComData() { ComName = mc.ComName };
                                    MapComData mc4 = new MapComData() { ComName = mc.ComName };
                                    MapComData mc5 = new MapComData() { ComName = mc.ComName };
                                    if (mc.ComPos.x <= 0)
                                    {
                                        mc2.ComPos= new Vector3(mc.ComPos.x + 3.36f, mc.ComPos.y, 0);
                                        mc3.ComPos = new Vector3(mc.ComPos.x + 6.72f, mc.ComPos.y, 0);
                                        mc4.ComPos= new Vector3(mc.ComPos.x - 3.36f, mc.ComPos.y, 0);
                                        mc5.ComPos= new Vector3(mc.ComPos.x - 6.72f, mc.ComPos.y, 0);
                                    }
                                    else
                                    {
                                        mc2.ComPos = new Vector3(mc.ComPos.x + 3.36f, mc.ComPos.y, 0);
                                        mc3.ComPos = new Vector3(mc.ComPos.x - 6.72f, mc.ComPos.y, 0);
                                        mc4.ComPos = new Vector3(mc.ComPos.x - 3.36f, mc.ComPos.y, 0);
                                        mc5.ComPos = new Vector3(mc.ComPos.x + 6.72f, mc.ComPos.y, 0);
                                    }
                                    MapCfgArr.Add(mc2);
                                    MapCfgArr.Add(mc3);
                                    MapCfgArr.Add(mc4);
                                    MapCfgArr.Add(mc5);
                                }
                            }
                            
                            break;
                    }
                }
                MapCfgArr.Add(mc);
            }
        }
    }

    #endregion

    #region InitAnimalCfg
    //存放识别的动物信息
    public List<AnimalComData> AnimalCfgArr = new List<AnimalComData>();

    //TODO 还需根据动物格式修改
    public void InitAnimalData(string path)
    {
        //获取xml文件
        TextAsset xml = Resources.Load<TextAsset>(path);
        if (!xml)
        {
            Debug.LogError("地图组件信息不存在");
        }
        else
        {
            //建立xml文档，并从xml中读取内容
            XmlDocument doc = new XmlDocument();
            doc.LoadXml(xml.text);
            //将文档内容转化为一个节点列表
            XmlNodeList nodLst = doc.SelectSingleNode("animals").ChildNodes;

            //遍历每个节点
            //如果当前节点的ID等于null,则代表遍历结束
            for (int i = 0; i < nodLst.Count; i++)
            {
                XmlElement ele = nodLst[i] as XmlElement;

                if (ele.GetAttributeNode("ID") == null)
                {
                    continue;
                }

                AnimalComData mc = new AnimalComData();

                foreach (XmlElement e in nodLst[i].ChildNodes)
                {
                    switch (e.Name)
                    {
                        case "AnimalCategory":
                            mc.AnimalName = e.InnerText;
                            break;
                        case "DetectionPos":
                            string[] valarr = Regex.Split(e.InnerText, "\\s+", RegexOptions.IgnoreCase);
                            if (valarr[0] == "[")
                            {
                                valarr[4] = valarr[4].Substring(0, valarr[1].Length - 1);
                                float width = (float.Parse(valarr[3]) - float.Parse(valarr[1])) / 2;
                                float height = (float.Parse(valarr[4]) - float.Parse(valarr[2])) / 2;
                                Vector3 varVec = new Vector3(float.Parse(valarr[1])+width/2, float.Parse(valarr[2])+height/2, 0f);
                                mc.AnimalPos = varVec;
                                break;
                            }
                            else
                            {
                                valarr[0] = valarr[0].Substring(1);
                                valarr[3] = valarr[3].Substring(0, valarr[3].Length - 1);
                                float width = (float.Parse(valarr[2]) - float.Parse(valarr[0])) / 2;
                                float height = (float.Parse(valarr[3]) - float.Parse(valarr[1])) / 2;
                                Vector3 varVec = new Vector3(float.Parse(valarr[0]) + width/2, float.Parse(valarr[1]) + height/2, 0f);
                                mc.AnimalPos = varVec;
                                break;
                            }
                        case "ImageSize":
                            string[] isarr = e.InnerText.Split();
                            isarr[0] = isarr[0].Substring(1, isarr[0].Length - 2);
                            isarr[1] = isarr[1].Substring(0, isarr[1].Length - 1);

                            float pox = (mc.AnimalPos.x * 100 / (float.Parse(isarr[1]) / 2)) - 100;
                            float poy = 100 - (mc.AnimalPos.y * 100 / (float.Parse(isarr[0]) / 2));
                            mc.AnimalPos = new Vector3((float)(pox * 0.01 * MapSizeX), (float)(poy * 0.01 * MapSizeY), 0);
                            //if (mc.ComName.Equals("house") || mc.ComName.Equals("fence"))
                            //{
                            //    mc.ComPos = new Vector3(mc.ComPos.x, mc.ComPos.y - 1.40f, 0);
                            //}
                            //else if (mc.ComName.Equals("tree"))
                            //{
                            //    mc.ComPos = new Vector3(mc.ComPos.x, mc.ComPos.y - 0.56f, 0);
                            //}
                            mc.AnimalPos = new Vector3(mc.AnimalPos.x, mc.AnimalPos.y - 1.0f, 0);
                            break;
                    }
                }
                AnimalCfgArr.Add(mc);
            }
        }
    }
    #endregion
}

public class MapComData
{
    public string ComName;
    public Vector3 ComPos;
    public float width=0;
}

public class AnimalComData
{
    public string AnimalName;
    public Vector3 AnimalPos;
}

