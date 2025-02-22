using UnityEngine;

public class QuickUseSlot : MonoBehaviour
{
    public Item item;

    public void UseItem()
    {
        if (item != null)
        {
            Debug.Log("Using " + item.name);
            // Implement item use logic here
        }
    }
}
