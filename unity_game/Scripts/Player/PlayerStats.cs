using UnityEngine;

public class PlayerStats : MonoBehaviour
{
    public int currentHealth;
    public int maxHealth;
    public int level = 1;
    public int experience = 0;
    public int strength = 10;
    public int dexterity = 10;
    public int intelligence = 10;
    public Inventory inventory = new Inventory();

    public void AddExperience(int xp)
    {
        experience += xp;
        CheckForLevelUp();
    }

    private void CheckForLevelUp()
    {
        if (experience >= 100 * level)
        {
            level++;
            strength += 5;
            Debug.Log("Leveled up! Level " + level);
        }
    }
}
