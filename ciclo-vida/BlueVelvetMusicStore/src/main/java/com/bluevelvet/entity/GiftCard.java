/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Entity class representing a Gift Card.
 * @us US-0907 Enter gift card information - Granularity: Entity Definition
 * @us US-0907 View gift card balance - Granularity: Entity Definition
 */
package com.bluevelvet.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * @brief Represents a Gift Card in the system.
 */
@Entity
@Table(name = "gift_cards")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class GiftCard {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(unique = true, nullable = false)
    private String code;

    @NotNull
    @PositiveOrZero
    @Column(nullable = false)
    private BigDecimal balance;

    @Column(name = "is_active")
    private boolean isActive = true;

    // Could link to a User if assigned, but requirement implies generic entry or
    // check.
}
