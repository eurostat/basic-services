/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.BasicServicesValidation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

/**
 * Check the country CSV files are complant with the specs.
 * 
 * @author julien Gaffuri
 *
 */
public class HealthcareValidation {

	//run validation process for each country
	public static void main(String[] args) {
		System.out.println("Start");
		for(String cc : HealthcareUtil.ccs) {
			System.out.println("*** " + cc);
			ArrayList<Map<String, String>> data = CSVUtil.load(HealthcareUtil.path + cc+"/"+cc+".csv");
			System.out.println(data.size());
			validate(data, cc, HealthcareUtil.cols_);
		}
		System.out.println("End");
	}

	//validate 
	public static void validate(Collection<Map<String, String>> data, String cc, List<String> cols_) {
		boolean b;

		//validation on all aspects common to other basic services
		BasicServicesValidation.validate(data, cc, cols_);

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
