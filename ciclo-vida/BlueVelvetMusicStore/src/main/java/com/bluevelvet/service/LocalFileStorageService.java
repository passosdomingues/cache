/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Implementation of FileStorageService for local file system.
 * @us US-1306 Create category of products - Granularity: Service Implementation
 */
package com.bluevelvet.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

/**
 * @brief Service for storing files locally.
 */
@Service
public class LocalFileStorageService implements FileStorageService {

    @Value("${app.upload.dir:uploads}")
    private String uploadDir;

    /**
     * @brief Saves a file to the local file system.
     * @param file The file to save.
     * @return The unique name of the saved file.
     * @throws IOException If an I/O error occurs.
     */
    @Override
    public String saveFile(MultipartFile file) throws IOException {
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null) {
            throw new IOException("File name cannot be null");
        }
        String fileName = StringUtils.cleanPath(originalFilename);
        String uniqueFileName = UUID.randomUUID().toString() + "_" + fileName;

        Path uploadPath = Paths.get(uploadDir);

        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        try (InputStream inputStream = file.getInputStream()) {
            Path filePath = uploadPath.resolve(uniqueFileName);
            Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
            return uniqueFileName;
        } catch (IOException ioe) {
            throw new IOException("Could not save image file: " + fileName, ioe);
        }
    }

    /**
     * @brief Deletes a file from the local file system.
     * @param fileName The name of the file to delete.
     */
    @Override
    public void deleteFile(String fileName) {
        // Implementation for deleting file locally
        // For now, we can just log it or actually delete it
        try {
            Path filePath = Paths.get(uploadDir).resolve(fileName);
            Files.deleteIfExists(filePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
