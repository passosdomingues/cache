/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Repository for Gift Card operations.
 * @us US-0907 Enter gift card information - Granularity: Data Access
 * @us US-0907 View gift card balance - Granularity: Data Access
 */
package com.bluevelvet.repository;

import com.bluevelvet.entity.GiftCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * @brief Data access operations for Gift Cards.
 */
@Repository
public interface GiftCardRepository extends JpaRepository<GiftCard, Long> {
    Optional<GiftCard> findByCode(String code);
}
