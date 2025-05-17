"use client";

import { useState } from "react";
import { Button } from "./ui/button";

type FilterKey = "position" | "user_fields" | "chain" | "city";

type Props = {
  selectedFilters: {
    position: string;
    user_fields: string;
    chain: string;
    city: string;
  };
  setSelectedFilters: React.Dispatch<
    React.SetStateAction<{
      position: string;
      user_fields: string;
      chain: string;
      city: string;
    }>
  >;
  filterOptions: {
    positions: string[];
    user_fields: string[];
    chains: string[];
    cities: string[];
  };
};

export default function FilterSection({
  selectedFilters,
  setSelectedFilters,
  filterOptions,
}: Props) {
  const [activeCategory, setActiveCategory] = useState<FilterKey | null>(null);

  const filters = [
    { id: "position", title: "POSITION", options: filterOptions.positions },
    {
      id: "user_fields",
      title: "Verticals",
      options: filterOptions.user_fields,
    },
    { id: "chain", title: "CHAIN ECOSYSTEM", options: filterOptions.chains },
    { id: "city", title: "CITY", options: filterOptions.cities },
  ];

  const toggleFilter = (categoryId: FilterKey, option: string) => {
    setSelectedFilters((prev) => ({
      ...prev,
      [categoryId]: prev[categoryId] === option ? "" : option,
    }));
  };

  const isFilterSelected = (categoryId: FilterKey, option: string) =>
    selectedFilters[categoryId] === option;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2 justify-center">
        {filters.map((category) => (
          <Button
            key={category.id}
            onClick={() =>
              setActiveCategory(
                activeCategory === category.id
                  ? null
                  : (category.id as FilterKey)
              )
            }
            className={`rounded-full ${
              activeCategory === category.id
                ? "bg-red-500 text-white"
                : "bg-black text-white"
            }`}
          >
            {category.title}
          </Button>
        ))}
      </div>

      {activeCategory && (
        <div className="flex flex-wrap gap-2 justify-center mt-4">
          {filters
            .find((c) => c.id === activeCategory)
            ?.options.map((option) => (
              <Button
                key={option}
                onClick={() => toggleFilter(activeCategory, option)}
                className={`rounded-full ${
                  isFilterSelected(activeCategory, option)
                    ? "bg-red-500 text-white"
                    : "bg-white text-black hover:text-white"
                }`}
              >
                {option}
              </Button>
            ))}
        </div>
      )}
    </div>
  );
}
