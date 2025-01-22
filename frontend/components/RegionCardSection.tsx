import { Region } from "@/types";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";
import RegionCard from "./RegionCard";

interface RegionCardSectionProps {
  title: string;
  apiUrl: string;
}

const RegionCardSection: React.FC<RegionCardSectionProps> = async ({
  title,
  apiUrl,
}) => {
  const data: Region[] = await fetch(apiUrl).then((res) => res.json());

  return (
    <div className="flex flex-col gap-2">
      <h2 className="font-bold text-2xl">{title}</h2>
      <Carousel className="w-full">
        <CarouselContent className="-ml-1 py-2 pr-4">
          {data.slice(0, 9).map((item, index) => (
            <CarouselItem
              key={index}
              className="pl-4 basis-full sm:basis-1/2 md:basis-1/3 lg:basis-1/4 xl:basis-1/5 2xl:basis-1/6"
            >
              <div className="p-1 flex items-center">
                <RegionCard data={item} />
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
};

export default RegionCardSection;
