/****************************************************
    文件：Common.cs
    作者：XINWEI DUAN
    邮箱: 418563981@qq.com
    日期：#CreateTime#
    功能：Nothing
*****************************************************/

using System.Collections.Generic;
using UnityEngine;

public class Common : MonoBehaviour 
{
    public static Common Instance;




    private void Awake()
    {
        Instance = this;
    }

    private Dictionary<string, GameObject> PrefabsArr = new Dictionary<string, GameObject>();

    public GameObject GetPrefabs(string path, bool cache = false)
    {
        GameObject prefab = null;
        if (!PrefabsArr.TryGetValue(path, out prefab))
        {
            prefab = Resources.Load<GameObject>(path);
            if (cache)
            {
                PrefabsArr.Add(path, prefab);
            }
        }

        GameObject go = null;
        if (prefab != null)
        {
            go = Instantiate(prefab);
        }
        return go;
    }
}