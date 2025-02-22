using UnityEngine;

[System.Serializable]
public class Item
{
    public string name;
    public string itemType;
    public Sprite icon;
    public bool stackable;
    public int stackSize = 1;
}
