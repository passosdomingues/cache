/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Controller for Gift Card operations.
 * @us US-0907 Enter gift card information - Granularity: API Endpoint
 * @us US-0907 View gift card balance - Granularity: API Endpoint
 */
package com.bluevelvet.controller;

import com.bluevelvet.entity.GiftCard;
import com.bluevelvet.payload.response.MessageResponse;
import com.bluevelvet.service.GiftCardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;

/**
 * @brief REST Endpoints for Gift Cards.
 */
@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/giftcards")
@RequiredArgsConstructor
public class GiftCardController {

    private final GiftCardService giftCardService;

    /**
     * @brief Views the balance of a gift card.
     * @param code The gift card code.
     * @return Balance if found.
     */
    @GetMapping("/{code}/balance")
    public ResponseEntity<?> getBalance(@PathVariable String code) {
        Optional<BigDecimal> balance = giftCardService.getBalance(code);
        if (balance.isPresent()) {
            return ResponseEntity.ok(Map.of("code", code, "balance", balance.get()));
        } else {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error: Invalid or inactive gift card code."));
        }
    }

    /**
     * @brief Enters gift card information (Validation).
     * @param request Map containing "code".
     * @return Gift card details if valid.
     */
    @PostMapping("/validate")
    public ResponseEntity<?> validateGiftCard(@RequestBody Map<String, String> request) {
        String code = request.get("code");
        Optional<GiftCard> giftCard = giftCardService.getGiftCard(code);
        if (giftCard.isPresent()) {
            return ResponseEntity.ok(giftCard.get());
        } else {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error: Invalid gift card."));
        }
    }
}
