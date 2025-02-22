using UnityEngine;

public class PressurePlate : MonoBehaviour
{
    public GameObject doorToOpen;
    private bool isPressed = false;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player") && !isPressed)
        {
            isPressed = true;
            doorToOpen.SetActive(false);
            Debug.Log("Pressure plate pressed!");
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player") && isPressed)
        {
            isPressed = false;
        }
    }
}
