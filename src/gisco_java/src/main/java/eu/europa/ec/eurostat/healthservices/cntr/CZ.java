package eu.europa.ec.eurostat.healthservices.cntr;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.healthservices.HCUtil;
import eu.europa.ec.eurostat.healthservices.Validation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil;

public class CZ {

	private static final String cc = "CZ";

	public static void main(String[] args) {
		System.out.println("Start");

		//load data
		CSVFormat cf = CSVFormat.DEFAULT.withDelimiter(';').withFirstRecordAsHeader();
		List<Map<String, String>> data = CSVUtil.load(HCUtil.path + "CZ/export-2020-04.csv", cf);
		System.out.println(data.size());

		//filter
		data = data.stream().filter(
				d -> {
					String fType = d.get("DruhZarizeni");
					return
							//Hospital
							fType.equals("Nemocnice")
							//Hospital aftercare
							|| fType.equals("Nemocnice následné péèe")
							//Hospital for the long-term (LDN)
							|| fType.equals("Léèebna pro dlouhodobì nemocné (LDN)")
							//Medical Center
							//|| fType.equals("Zdravotnické støedisko")
							//Health care in social institutions p.
							//|| fType.equals("Zdravotní péèe v ústavech sociální p.")
							//Home health care
							//|| fType.equals("Domácí zdravotní péèe") 
							;
				}).collect(Collectors.toList());
		System.out.println(data.size());

		//remove columns
		CSVUtil.removeColumn(data,
				"ZdravotnickeZarizeniId",
				"PCZ",
				"PCDP",
				"DruhZarizeniKod",
				"Kraj",
				"KrajCode",
				"Okres",
				"OkresCode",
				"SpravniObvod",
				"PoskytovatelFax",
				"DatumZahajeniCinnosti",
				"IdentifikatorDatoveSchranky",
				"PoskytovatelNazev",
				"Ico",
				"TypOsoby",
				"PravniFormaKod",
				"RUIANKod",
				"ORPKodUZIS",
				"ORP",
				"KrajCodeSidlo",
				"KrajSidlo",
				"OkresCodeSidlo",
				"OkresSidlo",
				"PscSidlo","ObecSidlo",
				"UliceSidlo",
				"CisloDomovniOrientacniSidlo",
				"OborPece",
				"FormaPece",
				"DruhPece",
				"OdbornyZastupce",
				"LastModified"
				);

		//id
		CSVUtil.renameColumn(data, "KodZZ", "id");
		//hospital_name
		CSVUtil.renameColumn(data, "NazevCely", "hospital_name");
		//facility_type
		CSVUtil.renameColumn(data, "DruhZarizeni", "facility_type");
		//specs_list
		CSVUtil.renameColumn(data, "DruhZarizeniSekundarni", "list_specs");

		CSVUtil.renameColumn(data, "Obec", "city");
		CSVUtil.renameColumn(data, "Psc", "postcode");
		CSVUtil.renameColumn(data, "Ulice", "street");
		CSVUtil.renameColumn(data, "CisloDomovniOrientacni", "house_number");

		CSVUtil.renameColumn(data, "PoskytovatelTelefon", "tel");
		CSVUtil.renameColumn(data, "PoskytovatelEmail", "email");
		CSVUtil.renameColumn(data, "PoskytovatelWeb", "url");

		//lon,lat
		for(Map<String, String> d : data) {
			var gps = d.get("GPS");
			if(gps.isEmpty()) {
				d.put("lat", "0");
				d.put("lon", "0");
				d.put("geo_qual", "3");
			} else {
				String[] parts = gps.split(" ");
				d.put("lat", parts[0]);
				d.put("lon", parts[1]);
				d.put("geo_qual", "1");
			}
		}
		CSVUtil.removeColumn(data, "GPS");

		CSVUtil.addColumn(data, "cc", cc);
		CSVUtil.addColumn(data, "ref_date", "01/04/2020");

		CSVUtil.addColumn(data, "emergency", "");
		CSVUtil.addColumn(data, "public_private", "");

		//TODO geocode missing ones

		Validation.validate(data, cc);

		CSVUtil.save(data, HCUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path+cc + "/"+cc+".gpkg", ProjectionUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
