package eu.europa.ec.eurostat.basicservices.healthcare.cntr;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.healthcare.HCUtil;
import eu.europa.ec.eurostat.basicservices.healthcare.Validation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.services.ServicesGeocoding;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil;

public class HU {

	private static final String cc = "HU";

	public static void main(String[] args) {
		System.out.println("Start");

		format();

		System.out.println("End");
	}

	private static void format() {

		//load data
		CSVFormat cf = CSVFormat.DEFAULT.withDelimiter('\t').withFirstRecordAsHeader();
		List<Map<String, String>> data = CSVUtil.load(HCUtil.path + "HU/NEAK_Fin_2020.01_02.csv", cf);
		System.out.println(data.size());

		//filter
		data = data.stream().filter(
				d ->
				! d.get("Aktív fekvőbeteg-szakellátás").isEmpty()
				//&& ! d.get("Járó és - vagy fekvőbeteg-szakellátás").isEmpty()
				).collect(Collectors.toList());
		System.out.println(data.size());

		//remove columns
		CSVUtil.removeColumn(data,
				"Megyekód",
				"Megye név", //county name. keep it for address?
				"Pénzügyi típus kódja - megnevezése (2017.01.01-től)", "a", "Tulajdonos", "Vezető", "Beosztás",
				"Háziorvosi szolgálat",
				"Háziorvosi ügyelet",
				"Iskola egészségügyi ellátás",
				"Védőnői ellátás",
				"Anya-gyermek- és csecsemővédelem",
				"Mozgó szakorvosi szolgálat",
				"Fogászati ellátás",
				"Gondozás",
				"Otthoni szakápolás",
				"Betegszállítás",
				"Halottszálítás",
				"Művesekezelés",
				"Működési költségelőleg",
				"Célelőirányzat",
				"Mentés",
				"Laboratóriumi ellátás",
				"Járóbeteg-szakellátás",
				"CT",
				"Aktív fekvőbeteg-szakellátás",
				"Krónikus fekvőbeteg-szakellátás",
				"IM - BVOP",
				"Várólista csökk. és szakmapol. célok",
				"Extra finanszírozás",
				"Nagyértékű gyógyszerfin.",
				"Speciális finanszírozás",
				"Összesen", //this is the total financing? Indicator for capacity?

				//Active inpatient specialist care
				"Aktív fekvőbeteg-szakellátás",
				//Inpatient care
				"Fekvőbeteg-szakellátás",
				//Outpatient and - or inpatient specialist care
				"Járó és - vagy fekvőbeteg-szakellátás",
				//Outpatient care
				"Járóbeteg-szakellátás",
				//CT only
				"Csak CT",
				//Labor only
				"Csak Labor",
				//Just Walking
				"Csak Járó",
				//Active only
				"Csak Aktív",
				//Only Chronic
				"Csak Krónikus"
				);

		CSVUtil.renameColumn(data, "Int.kód", "id");
		CSVUtil.renameColumn(data, "Irányítószám", "postcode");
		CSVUtil.renameColumn(data, "Település", "city");

		for(Map<String, String> d : data) {

			//hospital name
			//remove city name in the end
			{
				var hn = d.get("Szolgáltató");
				var parts = hn.split(", ");
				if(parts.length > 1 && parts[parts.length-1].split("\\s+").length == 1)
					hn = hn.replace(", "+parts[parts.length-1], "");
				d.put("hospital_name", hn);
			}

			//split street/housenumber
			{
				String utca = d.get("Utca");
				var parts = utca.split(" ");
				var hn = parts[parts.length-1];
				//check if last part contains digits
				if(hn.matches(".*\\d.*")) {
					String street = utca.replace(hn, "").trim();
					d.put("street", street);
					d.put("house_number", hn.replace(".", ""));
				} else {
					d.put("street", utca);
					d.put("house_number", "");
				}
			}

			//tel
			d.put("tel", d.get("Tel.körzet") + "-" + d.get("Telefonszám"));
		}
		CSVUtil.removeColumn(data, "Szolgáltató");
		CSVUtil.removeColumn(data, "Utca");
		CSVUtil.removeColumn(data, "Telefonszám");
		CSVUtil.removeColumn(data, "Tel.körzet");

		CSVUtil.addColumn(data, "cc", cc);
		CSVUtil.addColumn(data, "ref_date", "01/02/2020");

		CSVUtil.addColumn(data, "site_name", "");
		CSVUtil.addColumn(data, "emergency", "");
		CSVUtil.addColumn(data, "public_private", "");
		CSVUtil.addColumn(data, "geo_qual", "3");
		CSVUtil.addColumn(data, "lat", "0");
		CSVUtil.addColumn(data, "lon", "0");

		//join number of beds
		CSVUtil.addColumn(data, "cap_beds", "");
		List<Map<String, String>> nbbeds = CSVUtil.load(HCUtil.path + "HU/number_of_beds.csv");
		System.out.println(nbbeds.size());
		CSVUtil.join(data, "id", nbbeds, "id", false);

		Validation.validate(data, cc);

		LocalParameters.loadProxySettings();
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HCUtil.cols, "");
		Validation.validate(data, cc);
		CSVUtil.save(data, HCUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path+cc + "/"+cc+".gpkg", ProjectionUtil.getWGS_84_CRS());
	}

}
