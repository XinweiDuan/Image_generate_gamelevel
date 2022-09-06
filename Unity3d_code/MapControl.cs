/****************************************************
    文件：MapControl.cs
    作者：XINWEI DUAN
    邮箱: 418563981@qq.com
    日期：#CreateTime#
    功能：Nothing
*****************************************************/

using System.Collections.Generic;
using UnityEngine;

public class MapControl : MonoBehaviour 
{
    public static MapControl Instance;
    public Transform Parent;
    private void Awake()
    {
        Instance = this;
    }

    public void Init(List<MapComData> MapCfgArr,List<AnimalComData> AnimalCfgArr)
    {
        GenerateMap(MapCfgArr,AnimalCfgArr);
    }

    private void GenerateMap(List<MapComData> MapCfgArr,List<AnimalComData> AnimalCfgArr)
    {
        //生成地面效果
        GameObject ground =Common.Instance.GetPrefabs(PathDefine.ground,true);
        ground.transform.position = Vector3.zero;

        //根据list存储信息生成组件信息
        foreach(var item in MapCfgArr)
        {
            string path="";
            switch (item.ComName)
            {
                case "tree":
                    path = PathDefine.tree;
                    break;
                case "house":
                    path = PathDefine.house;
                    break;
                case "fence":
                    path = PathDefine.fence;
                    break;
            };
            GameObject go = Common.Instance.GetPrefabs(path, true);
            //go.transform.SetParent(Parent);
            go.transform.position= item.ComPos;
        }

        //TODO 生成动物信息
        foreach (var item in AnimalCfgArr)
        {
            string path = "";
            string brand = item.AnimalName.Substring(item.AnimalName.Length - 1,1);
            switch (brand)
            {
                case "马":
                    path = PathDefine.wolf;
                    break;
                case "牛":
                    path = PathDefine.cow;
                    break;
                case "鸡":
                    path = PathDefine.fence;
                    break;
                case "羊":
                    path = PathDefine.fence;
                    break;
            };
            GameObject go = Common.Instance.GetPrefabs(path, true);
            //go.transform.SetParent(Parent);
            go.transform.position = item.AnimalPos;
        }
    }

    


}