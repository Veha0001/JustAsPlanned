#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef __WIN32
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

// Function to patch the binary file
void patchBinary(
    const std::string &inputFile, const std::string &outputFile,
    const std::vector<std::pair<std::string, std::string>> &bytePairs) {
  std::ifstream inFile(inputFile, std::ios::binary);
  if (!inFile) {
    throw std::runtime_error("Error: Input file '" + inputFile +
                             "' not found.");
  }

  std::vector<uint8_t> data((std::istreambuf_iterator<char>(inFile)),
                            std::istreambuf_iterator<char>());
  inFile.close();

  for (const auto &pair : bytePairs) {
    std::vector<uint8_t> orig = hexStringToBytes(pair.first);
    std::vector<uint8_t> repl = hexStringToBytes(pair.second);

    size_t index = patternScan(data, orig);
    if (index != static_cast<size_t>(-1)) {
      std::ostringstream offsetStream;
      offsetStream << "0x" << std::hex << std::uppercase << index;

      printColored("[FOUND] Match for pattern: " +
                       bytesToHexString(orig, true, true),
                   GREEN, true);
      printColored("[OFFSET] At: " + offsetStream.str(), CYAN, true);
      printColored("[PATCH] Replaced with: " +
                       bytesToHexString(repl, true, false),
                   MAGENTA, true);

      // Replace the bytes in the data
      std::copy(repl.begin(), repl.end(), data.begin() + index);
    } else {
      printColored("No matches found for pattern: " + pair.first, RED);
    }
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

int main() {
// Set console title
#ifdef __WIN32
  SetConsoleTitle("JustAsPlanned");
#endif
  // Byte sequences (original, replacement)
  std::vector<std::pair<std::string, std::string>> byteSequences = {
      {"40 53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 "
       "?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? "
       "?? ?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? "
       "5B E9 ?? ?? ?? ?? CC CC CC CC CC 48 83 EC ?? 33 C9 E8 ?? ?? ?? ?? 80 "
       "3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? "
       "?? ?? ?? 48 8B 05 ?? ?? ?? ?? 33 D2 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? "
       "48 83 C4 ?? E9 ?? ?? ?? ?? CC CC CC CC CC CC CC CC CC CC CC CC CC 40 "
       "53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? "
       "8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? "
       "?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? 5B "
       "E9 ?? ?? ?? ?? CC CC CC CC CC 48 83 EC ?? 33 C9 E8 ?? ?? ?? ?? 80 3D "
       "?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? "
       "?? ?? 48 8B 05 ?? ?? ?? ?? 33 D2 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 "
       "83 C4 ?? E9 ?? ?? ?? ?? CC CC CC CC CC CC CC CC CC CC CC CC CC 48 83 "
       "EC",
       "48 B8 01 00 00 00 00 00 00 00 C3"},
      {"40 53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 "
       "?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? "
       "?? ?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? "
       "5B E9 ?? ?? ?? ?? CC CC CC CC CC 40 55 53",
       "B8 85 47 DE 63 C3"},
      {"48 83 EC ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? "
       "?? C6 05 ?? ?? ?? ?? ?? 48 8B 0D ?? ?? ?? ?? F6 81 ?? ?? ?? ?? ?? 74 "
       "?? 83 B9 ?? ?? ?? ?? ?? 75 ?? E8 ?? ?? ?? ?? 33 C9 E8 ?? ?? ?? ?? 84 "
       "C0 0F 85",
       "48 B8 01 00 00 00 00 00 00 00 C3"}};

  try {
    patchBinary("GameAssembly.dll", "GameAssembly_patched.dll", byteSequences);
  } catch (const std::runtime_error &e) {
    std::cerr << e.what() << std::endl;
    goodbye();
    return 1;
  }
  // Prevent the console from closing immediately
  goodbye();
  return 0;
}
