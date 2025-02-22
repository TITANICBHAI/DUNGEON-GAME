using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System.Collections.Generic;
using System.Linq;

public class UIManager : MonoBehaviour, IPointerDownHandler, IBeginDragHandler, IEndDragHandler, IDragHandler, IDropHandler
{
    public PlayerStats playerStats;
    public GameObject inventoryPanel;
    public GameObject itemSlotPrefab;
    public GameObject quickUsePanel;
    public GameObject quickUseSlotPrefab;

    public Text healthText;
    public Text levelText;
    public Text strengthText;
    public Text dexterityText;
    public Text intelligenceText;

    public Transform inventoryGrid;
    private List<GameObject> itemSlots = new List<GameObject>();
    private GameObject draggedItemSlot;
    private Item draggedItem;

    void Start()
    {
        UpdateStatsUI();
        UpdateInventoryUI();
    }

    void Update()
    {
        UpdateStatsUI();
    }

    void UpdateStatsUI()
    {
        healthText.text = "Health: " + playerStats.currentHealth + "/" + playerStats.maxHealth;
        levelText.text = "Level: " + playerStats.level;
        strengthText.text = "Strength: " + playerStats.strength;
        dexterityText.text = "Dexterity: " + playerStats.dexterity;
        intelligenceText.text = "Intelligence: " + playerStats.intelligence;
    }

    public void UpdateInventoryUI()
    {
        foreach (GameObject slot in itemSlots)
        {
            Destroy(slot);
        }
        itemSlots.Clear();

        foreach (Item item in playerStats.inventory.items)
        {
            GameObject newItemSlot = Instantiate(itemSlotPrefab, inventoryGrid);
            itemSlots.Add(newItemSlot);

            Image itemIcon = newItemSlot.transform.Find("ItemIcon").GetComponent<Image>();
            Text itemName = newItemSlot.transform.Find("ItemName").GetComponent<Text>();
            Text itemQuantity = newItemSlot.transform.Find("ItemQuantity").GetComponent<Text>();

            if (itemIcon != null) itemIcon.sprite = item.icon;
            if (itemName != null) itemName.text = item.name;
            if (itemQuantity != null && item.stackable)
            {
                itemQuantity.text = "x" + item.stackSize;
            }
        }
    }

    // Implement interface methods for drag and drop functionality
    public void OnPointerDown(PointerEventData eventData)
    {
        GameObject clickedObject = eventData.pointerCurrentRaycast.gameObject;
        if (clickedObject != null && clickedObject.CompareTag("ItemSlot"))
        {
            draggedItemSlot = clickedObject;
            int index = itemSlots.IndexOf(draggedItemSlot);
            if (index >= 0 && index < playerStats.inventory.items.Count)
            {
                draggedItem = playerStats.inventory.items[index];
            }
        }
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        if (draggedItemSlot != null)
        {
            draggedItemSlot.GetComponent<Image>().color = new Color(1f, 1f, 1f, 0.5f);
        }
    }

    public void OnDrag(PointerEventData eventData) { }

    public void OnEndDrag(PointerEventData eventData)
    {
        if (draggedItemSlot != null)
        {
            draggedItemSlot.GetComponent<Image>().color = Color.white;
            draggedItemSlot = null;
            draggedItem = null;
        }
    }

    public void OnDrop(PointerEventData eventData)
    {
        if (draggedItemSlot != null)
        {
            GameObject droppedObject = eventData.pointerCurrentRaycast.gameObject;
            if (droppedObject != null)
            {
                HandleItemDrop(droppedObject);
            }
            draggedItemSlot.GetComponent<Image>().color = Color.white;
            draggedItemSlot = null;
            draggedItem = null;
        }
    }

    private void HandleItemDrop(GameObject droppedObject)
    {
        if (droppedObject.CompareTag("ItemSlot"))
        {
            SwapItems(droppedObject);
        }
        else if (droppedObject.CompareTag("QuickUseSlot"))
        {
            AddItemToQuickUse(draggedItem);
        }
    }

    private void SwapItems(GameObject droppedObject)
    {
        int draggedIndex = itemSlots.IndexOf(draggedItemSlot);
        int droppedIndex = itemSlots.IndexOf(droppedObject);

        if (draggedIndex >= 0 && draggedIndex < playerStats.inventory.items.Count &&
            droppedIndex >= 0 && droppedIndex < playerStats.inventory.items.Count)
        {
            var temp = playerStats.inventory.items[draggedIndex];
            playerStats.inventory.items[draggedIndex] = playerStats.inventory.items[droppedIndex];
            playerStats.inventory.items[droppedIndex] = temp;
            UpdateInventoryUI();
        }
    }

    public void AddItemToQuickUse(Item item)
    {
        GameObject newQuickUseSlot = Instantiate(quickUseSlotPrefab, quickUsePanel.transform);
        Image itemIcon = newQuickUseSlot.transform.Find("ItemIcon").GetComponent<Image>();
        if (itemIcon != null)
        {
            itemIcon.sprite = item.icon;
        }
        newQuickUseSlot.GetComponent<QuickUseSlot>().item = item;
    }
}
