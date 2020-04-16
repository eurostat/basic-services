package eu.europa.ec.eurostat.healthservices.cntr;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.healthservices.HCUtil;
import eu.europa.ec.eurostat.healthservices.Validation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

public class HU {

	public static void main(String[] args) {
		System.out.println("Start");

		String cc = "HU";

		//load data
		CSVFormat cf = CSVFormat.DEFAULT.withDelimiter('\t').withFirstRecordAsHeader();
		List<Map<String, String>> data = CSVUtil.load(HCUtil.path + "HU/NEAK_Fin_2020.01_02.csv", cf);
		System.out.println(data.size());

		//filter
		data = data.stream().filter(d -> !d.get("Aktív fekvőbeteg-szakellátás").isEmpty()).collect(Collectors.toList());
		System.out.println(data.size());

		//remove columns
		for(String col : new String[]{
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
				"Összesen", //this is the total bidget? Indicator for capacity?

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
				"Csak Krónikus",
		})
			CSVUtil.removeColumn(data, col);

		CSVUtil.renameColumn(data, "Int.kód", "id");
		CSVUtil.renameColumn(data, "Szolgáltató", "hospital_name");
		CSVUtil.renameColumn(data, "Irányítószám", "postcode");
		CSVUtil.renameColumn(data, "Település", "city");
		CSVUtil.renameColumn(data, "Utca", "street");
		//CSVUtil.renameColumn(data, "", "");

		//tel
		for(Map<String, String> d : data) {
			//tel
			d.put("tel", d.get("Tel.körzet") + "-" + d.get("Telefonszám"));

			//System.out.println(d.get("hospital_name"));
		}
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

		Validation.validate(data, "HU");

		System.out.println("End");
	}

}
