/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Service logic for Gift Cards.
 * @us US-0907 Enter gift card information - Granularity: Business Logic
 * @us US-0907 View gift card balance - Granularity: Business Logic
 */
package com.bluevelvet.service;

import com.bluevelvet.entity.GiftCard;
import com.bluevelvet.repository.GiftCardRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.Optional;

/**
 * @brief Manages Gift Card business logic.
 */
@Service
@RequiredArgsConstructor
public class GiftCardService {

    private final GiftCardRepository giftCardRepository;

    /**
     * @brief Retrieves the balance of a gift card.
     * @param code The gift card code.
     * @return The balance if found and active.
     */
    public Optional<BigDecimal> getBalance(String code) {
        return giftCardRepository.findByCode(code)
                .filter(GiftCard::isActive)
                .map(GiftCard::getBalance);
    }

    /**
     * @brief Claims or checks a gift card code (Enter information).
     * @param code The gift card code.
     * @return The GiftCard entity if valid.
     */
    public Optional<GiftCard> getGiftCard(String code) {
        return giftCardRepository.findByCode(code)
                .filter(GiftCard::isActive);
    }

    // Additional methods for checkout processing would go here.
}
