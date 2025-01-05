#include <fstream>
#include <iomanip>
#include <iostream>
#include <nlohmann/json.hpp>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#endif

// Define colors for console output
enum Color {
  RESET = 0,
  RED = 31,
  GREEN = 32,
  YELLOW = 33,
  BLUE = 34,
  MAGENTA = 35,
  CYAN = 36,
  WHITE = 37
};

// Function to print colored text
void printColored(const std::string &text, Color color, bool bold = false) {
  std::cout << "\033[" << (bold ? "1;" : "") << color << "m" << text
            << "\033[0m" << std::endl;
}

void goodbye() {
#ifdef _WIN32
  std::cout << "Press Enter to continue...";
  std::cin.get();
#endif
}

// Function to convert bytes to a formatted hex string for display
std::string bytesToHexString(const std::vector<uint8_t> &bytes,
                             bool colored = true, bool allowWildcards = true) {
  std::ostringstream oss;
  for (size_t i = 0; i < bytes.size(); ++i) {
    if (i > 0)
      oss << " "; // Single space between bytes
    if (colored && allowWildcards && bytes[i] == 0x00) {
      oss << "\033[1;34m??\033[0m"; // Bold blue for wildcards
    } else {
      oss << "\033[34m" << std::hex << std::uppercase << std::setw(2)
          << std::setfill('0') << static_cast<int>(bytes[i]) << "\033[0m";
    }
  }
  return oss.str();
}

// Function to convert a string of hex bytes into a vector of integers
std::vector<uint8_t> hexStringToBytes(const std::string &hex) {
  std::vector<uint8_t> bytes;
  std::istringstream iss(hex);
  std::string byte;
  while (iss >> byte) {
    if (byte == "??") {
      bytes.push_back(0x00); // Placeholder for wildcard
    } else {
      bytes.push_back(static_cast<uint8_t>(std::stoi(byte, nullptr, 16)));
    }
  }
  return bytes;
}

// Function to search for a byte pattern in the given data
size_t patternScan(const std::vector<uint8_t> &data,
                   const std::vector<uint8_t> &pattern) {
  for (size_t i = 0; i <= data.size() - pattern.size(); ++i) {
    bool match = true;
    for (size_t j = 0; j < pattern.size(); ++j) {
      if (pattern[j] != 0x00 && pattern[j] != data[i + j]) {
        match = false;
        break;
      }
    }
    if (match) {
      return i; // Return the starting index of the match
    }
  }
  return static_cast<size_t>(-1); // Pattern not found
}

// Function to find offset by method name in the dump file
std::optional<size_t> findOffsetByMethodName(const std::string &methodName,
                                             const std::string &dumpPath) {
  std::ifstream dumpFile(dumpPath);
  if (!dumpFile.is_open()) {
    printColored("Error: Dump file '" + dumpPath + "' not found.", RED);
    return std::nullopt;
  }

  std::string line;
  std::regex offsetRegex(R"(Offset:\s*0x([0-9A-Fa-f]+))");
  std::string previousLine;

  while (std::getline(dumpFile, line)) {
    if (line.find(methodName) != std::string::npos) {
      if (!previousLine.empty()) {
        std::smatch match;
        if (std::regex_search(previousLine, match, offsetRegex)) {
          size_t offset = std::stoul(match[1].str(), nullptr, 16);
          printColored("Found " + methodName + " at Offset: 0x" +
                           std::to_string(offset),
                       GREEN);
          return offset;
        }
      }
      printColored("Warning: No offset found for " + methodName + ".", YELLOW);
      return std::nullopt;
    }
    previousLine = line;
  }
  return std::nullopt;
}

// Function to patch the binary file
void patchBinary(const std::string &inputFile, const std::string &outputFile,
                 const nlohmann::json &patchList, const std::string &dumpPath) {
  std::ifstream inFile(inputFile, std::ios::binary);
  if (!inFile) {
    throw std::runtime_error("Error: Input file '" + inputFile + "' not found.");
  }

  std::vector<uint8_t> data((std::istreambuf_iterator<char>(inFile)),
                            std::istreambuf_iterator<char>());
  inFile.close();

  for (const auto &patch : patchList) {
    size_t offset = 0;

    if (patch.contains("method_name")) {
      auto result = findOffsetByMethodName(patch["method_name"], dumpPath);
      if (!result) {
        printColored("Warning: Method '" + patch["method_name"].get<std::string>() +
                         "' not found. Skipping patch.",
                     YELLOW);
        continue;
      }
      offset = *result;
    } else if (patch.contains("offset")) {
      offset = std::stoul(patch["offset"].get<std::string>(), nullptr, 16);
    } else if (patch.contains("wildcard")) {
      std::vector<uint8_t> orig = hexStringToBytes(patch["wildcard"]);
      offset = patternScan(data, orig);
      if (offset == static_cast<size_t>(-1)) {
        printColored("Warning: No match found for wildcard pattern '" +
                         patch["wildcard"].get<std::string>() + "'. Skipping patch.",
                     YELLOW);
        continue;
      }
    } else {
      printColored("Warning: No valid patch definition found. Skipping.", YELLOW);
      continue;
    }

    if (offset >= data.size()) {
      printColored("Error: Offset 0x" + std::to_string(offset) +
                       " is out of range for the input file.",
                   RED);
      continue;
    }

    std::vector<uint8_t> repl = hexStringToBytes(patch["hex_code"]);
    printColored("Patching at Offset: 0x" + std::to_string(offset), GREEN);
    std::copy(repl.begin(), repl.end(), data.begin() + offset);
  }

  std::ofstream outFile(outputFile, std::ios::binary);
  if (!outFile) {
    throw std::runtime_error("Error: Could not write to output file '" +
                             outputFile + "'.");
  }
  outFile.write(reinterpret_cast<const char *>(data.data()), data.size());
  outFile.close();
  printColored("[DONE] Patched file saved as: " + outputFile, GREEN);
}

int main(int argc, char *argv[]) {
  std::string configPath = "config.json"; // Default configuration file name

  if (argc > 1) {
    configPath = argv[1]; // Use provided config path
  }

  nlohmann::json config;
  try {
    std::ifstream configFile(configPath);
    if (!configFile.is_open()) {
      printColored("Error: Configuration file '" + configPath + "' not found.", RED);
      goodbye();
      return 1;
    }
    configFile >> config;
  } catch (const std::exception &e) {
    printColored("Error loading configuration: " + std::string(e.what()), RED);
    goodbye();
    return 1;
  }

  // Extract necessary details
  std::string inputFilename = config["Patcher"]["input_file"];
  std::string dumpPath = config["Patcher"]["dump_file"];
  std::string outputFilename = config["Patcher"]["output_file"];
  auto patchList = config["Patcher"]["patches"];

  // Apply patches to binary
  try {
    patchBinary(inputFilename, outputFilename, patchList, dumpPath);
  } catch (const std::runtime_error &e) {
    printColored(e.what(), RED);
    goodbye();
    return 1;
  }

  // Prevent the console from closing immediately
  goodbye();
  return 0;
}