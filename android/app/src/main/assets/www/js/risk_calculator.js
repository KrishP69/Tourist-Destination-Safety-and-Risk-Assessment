// Client-Side Risk Calculator & Visual Indicator Utilities

function getTierDetails(tier) {
  if (tier.includes("Safe") || tier.includes("Low Risk")) {
    return {
      cssClass: "safe",
      color: "#10B981",
      verdictTitle: "Optimal Travel Conditions",
      verdictText: "Low crime rate, high municipal vigilance, reliable healthcare, and robust emergency services."
    };
  } else if (tier.includes("Moderate")) {
    return {
      cssClass: "moderate",
      color: "#F59E0B",
      verdictTitle: "Standard Traveler Caution",
      verdictText: "Normal travel safe with standard vigilance against pickpocketing, scams, and seasonal weather."
    };
  } else if (tier.includes("Caution")) {
    return {
      cssClass: "caution",
      color: "#F97316",
      verdictTitle: "Elevated Risk Caution",
      verdictText: "Elevated street crime or hazard alerts. Avoid solitary late-night transit; use authorized transport."
    };
  } else {
    return {
      cssClass: "critical",
      color: "#EF4444",
      verdictTitle: "Severe Travel Advisory",
      verdictText: "Severe hazard, high crime index, or emergency advisory active. Exercise extreme caution."
    };
  }
}
