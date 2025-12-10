/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Service interface for file storage operations.
 * @us US-1306 Create category of products - Granularity: Service Interface
 */
package com.bluevelvet.service;

import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;

/**
 * @brief Interface defining file storage operations.
 */
public interface FileStorageService {
    /**
     * @brief Saves a file.
     * @param file The file to save.
     * @return The name of the saved file.
     * @throws IOException If an I/O error occurs.
     */
    String saveFile(MultipartFile file) throws IOException;

    /**
     * @brief Deletes a file.
     * @param fileName The name of the file to delete.
     */
    void deleteFile(String fileName);
}
