#ifndef CONFIG_HPP
#define CONFIG_HPP

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <functional>
#include "policies/SchedulingPolicy.hpp"

/**
 * @brief Simulation configuration container
 */
class SimulationConfig {
public:
    // Basic parameters
    double targetOccupancy;
    std::vector<double> serviceRates;
    std::vector<double> arrivalRates;
    std::shared_ptr<SchedulingPolicy> schedulingPolicy;
    unsigned long randomSeed;
    std::string scenarioName;
    
    // Advanced parameters
    double simulationTime;
    double samplingInterval;
    int numQueues;
    std::string discardPolicy;
    unsigned long maxQueueSize;
    
    /**
     * @brief Default constructor
     */
    SimulationConfig();
    
    /**
     * @brief Calculate arrival rates from occupancy and service rates
     */
    void calculateArrivalRates();
    
    /**
     * @brief Validate configuration parameters
     * @throws std::invalid_argument if validation fails
     */
    void validate() const;
};

/**
 * @brief Configuration file parser and manager
 */
class ConfigManager {
private:
    std::map<std::string, std::string> configMap;
    
public:
    /**
     * @brief Load configuration from file
     * @param filename Configuration file path
     * @return SimulationConfig Parsed configuration
     */
    SimulationConfig loadFromFile(const std::string& filename);
    
    /**
     * @brief Load configuration from command line arguments
     * @param argc Argument count
     * @param argv Argument vector
     * @return SimulationConfig Parsed configuration
     */
    SimulationConfig loadFromCommandLine(int argc, char* argv[]);
    
    /**
     * @brief Save configuration to file
     * @param config Configuration to save
     * @param filename Output file path
     */
    static void saveToFile(const SimulationConfig& config, const std::string& filename);
    
    /**
     * @brief Generate default configuration
     * @return SimulationConfig Default configuration
     */
    static SimulationConfig generateDefault();
};

#endif // CONFIG_HPP