using UnityEngine;

public class Combat : MonoBehaviour
{
    public int attackDamage = 10;
    public float attackRange = 1f;

    public void Attack()
    {
        Collider[] colliders = Physics.OverlapSphere(transform.position, attackRange);
        foreach (Collider collider in colliders)
        {
            if (collider.CompareTag("Enemy"))
            {
                Debug.Log("Hit enemy for " + attackDamage + " damage!");
                Enemy enemy = collider.GetComponent<Enemy>();
                if (enemy != null)
                {
                    enemy.TakeDamage(attackDamage);
                }
            }
        }
    }

    void Update()
    {
        if (Input.GetButtonDown("Fire1"))
        {
            Attack();
        }
    }
}
