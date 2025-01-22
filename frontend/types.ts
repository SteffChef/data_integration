export type DiveSite = {
    id: number;
    title: string;
    categories: DiveSiteCategory[];
    animals: Animal[];
    rating: number;
    image_url: string;
    latitude: number;
    longitude: number;
    description?: string;
    region?: string;
};

export type DiveSiteCategory = {
    id: number;
    name: string;
    image_url: string;
}

export type DiveSiteRating = {
    "1":number;
    "2":number;
    "3":number;
    "4":number;
    "5":number;
}

export type Animal = {
    id:number;
    name: string;
    image_url: string;
}

export type AnimalRecommendation = {
    animal_id: number;
    animal_image_url: string;
    animal_name: string;
    dive_sites: DiveSite[];
    mean_predicted_rating: number;
}

export type Region = {
    first_image_url: string;
    region: string;
    region_score: number;
}