/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.BasicServicesValidation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

/**
 * Check if healthcare CSV files are compliant with the specs.
 * 
 * @author julien Gaffuri
 *
 */
public class Validation {

	/**
	 * run validation process for each country
	 * @param args 
	 */
	public static void main(String[] args) {
		System.out.println("Start");
		for(String cc : HealthcareUtil.ccs) {
			System.out.println("*** " + cc);
			ArrayList<Map<String, String>> data = CSVUtil.load(HealthcareUtil.path + cc+"/"+cc+".csv");
			System.out.println(data.size());
			validate(data, cc);
		}
		System.out.println("End");
	}

	/**
	 * Validate data for a specific country.
	 * 
	 * @param data
	 * @param cc
	 */
	public static void validate(Collection<Map<String, String>> data, String cc) {
		boolean b;

		//validation on all aspects common to other basic services
		BasicServicesValidation.validate(data, cc, HealthcareUtil.cols_);

		//TODO other tests ?
		//check list_specs
		//check empty columns

		//check emergency -yes/no
		b = BasicServicesValidation.checkValuesAmong(data, "emergency", "", "yes", "no");
		if(!b) System.err.println("Problem with emergency values for " + cc);

		//check public_private - public/private
		b = BasicServicesValidation.checkValuesAmong(data, "public_private", "", "public", "private");
		if(!b) System.err.println("Problem with public_private values for " + cc);

		//non null columns
		b = BasicServicesValidation.checkValuesNotNullOrEmpty(data, "hospital_name");
		if(!b) System.err.println("Missing values for hospital_name format for " + cc);

	}

}
