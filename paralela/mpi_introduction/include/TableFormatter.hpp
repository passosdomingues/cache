/**
 * @file TableFormatter.hpp
 * @brief Utility class for printing beautiful, aligned, colored tables in terminal output.
 */

#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <iomanip>

namespace DidacticMPI {

/**
 * @brief Terminal formatting utility for clear educational outputs.
 */
class TableFormatter {
public:
    static constexpr const char* RESET   = "\033[0m";
    static constexpr const char* BOLD    = "\033[1m";
    static constexpr const char* CYAN    = "\033[36m";
    static constexpr const char* GREEN   = "\033[32m";
    static constexpr const char* YELLOW  = "\033[33m";
    static constexpr const char* MAGENTA = "\033[35m";
    static constexpr const char* RED     = "\033[31m";

    /**
     * @brief Prints a stylized section banner for a lesson or module.
     * @param title The title of the lesson.
     * @param description Brief description of what is being demonstrated.
     */
    static void printHeader(const std::string& title, const std::string& description) {
        std::cout << "\n" << BOLD << CYAN << std::string(75, '=') << RESET << "\n";
        std::cout << BOLD << " 🎓 " << title << RESET << "\n";
        std::cout << "    " << description << "\n";
        std::cout << BOLD << CYAN << std::string(75, '=') << RESET << "\n";
    }

    /**
     * @brief Prints a footer for a lesson.
     */
    static void printFooter() {
        std::cout << BOLD << CYAN << std::string(75, '-') << RESET << "\n\n";
    }

    /**
     * @brief Formats a key-value row for quick summaries.
     */
    static void printKeyValue(const std::string& key, const std::string& value) {
        std::cout << "  • " << BOLD << std::left << std::setw(25) << key << RESET << ": " << value << "\n";
    }
};

} // namespace DidacticMPI
